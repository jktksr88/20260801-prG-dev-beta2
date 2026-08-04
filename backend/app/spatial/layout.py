from __future__ import annotations

from typing import Any
import math

from shapely.geometry import box, Polygon

from app.spatial.geometry import reserve_access_zone, polygon_payload


def _scan_coordinates(poly: Polygon, step: float, direction: str):
    minx, miny, maxx, maxy = poly.bounds
    xs = []
    x = minx
    while x <= maxx + 1e-9:
        xs.append(round(x, 4))
        x += step
    ys = []
    y = miny
    while y <= maxy + 1e-9:
        ys.append(round(y, 4))
        y += step
    if direction == "north":
        ys = list(reversed(ys))
    elif direction == "east":
        xs = list(reversed(xs))
    for yy in ys:
        row_xs = xs if int((yy - miny) / max(step, 0.01)) % 2 == 0 else list(reversed(xs))
        for xx in row_xs:
            yield xx, yy


def generate_layout(
    poly: Polygon,
    crop_allocations: list[dict[str, Any]],
    sun_direction: str = "north",
    entrance_edge: int | None = None,
    vertical_allowed: bool = True,
    tiered_rack_allowed: bool = False,
) -> dict:
    usable, access = reserve_access_zone(poly, entrance_edge)
    reserved_shapes = []
    placements = []
    adjustments = []
    vertical_modules = []

    # Taller crops are considered first so the sun-edge ordering stays deterministic.
    crops = sorted(
        crop_allocations,
        key=lambda crop: (-float(crop["parameters"].get("mature_height_cm", 0)), crop["slug"]),
    )

    for crop in crops:
        parameters = crop["parameters"]
        target = max(1, int(crop.get("target_quantity", 1)))
        spacing = max(0.10, float(parameters.get("preferred_spacing_cm", 25)) / 100)
        trellised = parameters.get("trellis_requirement") == "required" and vertical_allowed
        is_container = crop.get("surface") != "soil"
        container_spec = crop.get("container_spec") or {}

        if is_container:
            diameter = max(
                0.12,
                float(
                    container_spec.get("recommended_diameter_cm")
                    or parameters.get("minimum_container_diameter_cm")
                    or parameters.get("preferred_spacing_cm")
                    or 20
                )
                / 100,
            )
            width = diameter
            depth = diameter
            spacing_buffer = max(0.025, (spacing - diameter) / 2)
            structure_type = "pot"
        else:
            width = spacing
            depth = min(spacing, 0.42) if trellised else spacing
            spacing_buffer = 0.025
            structure_type = "soil"

        count = 0
        scan_step = max(0.05, min(width, depth) / 3)
        for x, y in _scan_coordinates(usable, scan_step, sun_direction):
            footprint = box(x, y, x + width, y + depth)
            if not usable.covers(footprint):
                continue
            reserved = footprint.buffer(spacing_buffer, join_style=2)
            if any(reserved.intersects(used) for used in reserved_shapes):
                continue
            reserved_shapes.append(reserved)
            count += 1
            placements.append(
                {
                    "placement_id": f"{crop['slug']}-{count}",
                    "crop_profile_id": crop["id"],
                    "slug": crop["slug"],
                    "name_en": crop["name_en"],
                    "name_id": crop["name_id"],
                    "category": crop.get("category"),
                    "x_m": round(x, 3),
                    "y_m": round(y, 3),
                    "width_m": round(width, 3),
                    "height_m": round(depth, 3),
                    "shape": "container" if is_container else "soil",
                    "structure_type": structure_type,
                    "container_spec": container_spec if is_container else None,
                    "trellis": trellised,
                    "tier": None,
                    "zone": "main",
                    "spacing_m": round(spacing, 3),
                }
            )
            if trellised:
                vertical_modules.append(
                    {
                        "type": "trellis",
                        "crop_slug": crop["slug"],
                        "x_m": round(x, 3),
                        "y_m": round(y, 3),
                        "width_m": round(width, 3),
                        "height_m": round(float(parameters.get("mature_height_cm", 150)) / 100, 2),
                        "support_strength": parameters.get("support_strength", "strong"),
                    }
                )
            if count >= target:
                break
        if count < target:
            adjustments.append(
                {
                    "code": "QUANTITY_REDUCED_TO_FIT",
                    "crop_slug": crop["slug"],
                    "requested": target,
                    "feasible": count,
                }
            )

    # A tiered stand is represented separately from ground pots.
    if tiered_rack_allowed:
        eligible = [
            crop
            for crop in crops
            if crop["parameters"].get("tiered_rack_eligible")
            and 2 in crop["parameters"].get("permitted_vertical_tiers", [])
        ]
        if eligible and poly.area >= 0.75:
            rack_width = min(0.8, max(0.5, math.sqrt(poly.area) * 0.35))
            assignments = []
            for tier, crop in zip([1, 2, 3], eligible[:3]):
                if tier in crop["parameters"].get("permitted_vertical_tiers", []):
                    assignments.append(
                        {
                            "tier": tier,
                            "crop_slug": crop["slug"],
                            "container_depth_cm": crop.get("container_spec", {}).get("recommended_depth_cm")
                            or crop["parameters"].get("minimum_container_depth_cm"),
                        }
                    )
            if assignments:
                minx, miny, maxx, _ = usable.bounds
                vertical_modules.append(
                    {
                        "type": "tiered_rack",
                        "x_m": round(minx, 3),
                        "y_m": round(miny, 3),
                        "module_width_m": round(rack_width, 2),
                        "module_depth_m": 0.35,
                        "module_height_m": 1.35,
                        "tiers": 3,
                        "assignments": assignments,
                        "warning": "Keep deep or heavy containers on Tier 1; confirm rack load rating and drainage.",
                    }
                )

    # Hanging pots are only suggested for compact, shallow-rooted crops when
    # vertical structures are allowed. They remain a separate module so their
    # support requirement is visible rather than silently counted as ground area.
    if vertical_allowed and any(crop.get("surface") != "soil" for crop in crops):
        hanging = next(
            (
                crop
                for crop in crops
                if crop["parameters"].get("tiered_rack_eligible")
                and float(crop["parameters"].get("mature_height_cm", 999)) <= 40
                and float(crop.get("container_spec", {}).get("recommended_depth_cm", 999)) <= 25
                and crop["parameters"].get("trellis_requirement") != "required"
            ),
            None,
        )
        if hanging and poly.area <= 4:
            vertical_modules.append(
                {
                    "type": "hanging_pot",
                    "crop_slug": hanging["slug"],
                    "recommended_diameter_cm": hanging.get("container_spec", {}).get("recommended_diameter_cm"),
                    "recommended_depth_cm": hanging.get("container_spec", {}).get("recommended_depth_cm"),
                    "support_warning": "Use a load-rated hook and keep the pot clear of the access path.",
                }
            )

    compost = None
    if poly.area >= 8:
        _, miny, maxx, _ = usable.bounds
        size = 0.45
        candidate = box(maxx - size, miny, maxx, miny + size)
        if usable.covers(candidate) and not any(candidate.intersects(used) for used in reserved_shapes):
            compost = {
                "x_m": round(maxx - size, 3),
                "y_m": round(miny, 3),
                "width_m": size,
                "height_m": size,
                "type": "compact_compost_point",
            }

    total_area = round(sum(p["width_m"] * p["height_m"] for p in placements), 2)
    return {
        "plot_boundary": polygon_payload(poly),
        "usable_boundary": polygon_payload(usable),
        "plot_area_m2": round(poly.area, 2),
        "usable_area_m2": round(usable.area, 2),
        "access_zone": polygon_payload(access) if access and not access.is_empty else None,
        "placements": placements,
        "vertical_modules": vertical_modules,
        "compost": compost,
        "occupied_area_m2": total_area,
        "adjustments": adjustments,
        "scale_unit": "metres",
        "sun_direction": sun_direction,
    }
