from __future__ import annotations

from typing import Any
import math

from shapely.geometry import box, Polygon

from app.spatial.geometry import reserve_access_zone, polygon_payload


# Conservative beta allow-list. These crops have compact or trailing growth and
# shallow enough container requirements in the current GROE metadata. A crop is
# still checked against actual pot depth, diameter, height and support rules.
HANGING_POT_PRIORITY = {
    "stroberi": 1,
    "mint": 2,
    "kangkung": 3,
    "selada": 4,
    "kemangi": 5,
    "seledri": 6,
    "daun-bawang": 7,
    "kucai": 8,
}


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


def _placement_box(placement: dict[str, Any]):
    return box(
        float(placement["x_m"]),
        float(placement["y_m"]),
        float(placement["x_m"]) + float(placement["width_m"]),
        float(placement["y_m"]) + float(placement["height_m"]),
    )


def _find_module_position(
    usable: Polygon,
    width: float,
    depth: float,
    occupied: list,
    sun_direction: str,
) -> tuple[float, float] | None:
    for x, y in _scan_coordinates(usable, 0.05, sun_direction):
        footprint = box(x, y, x + width, y + depth)
        if not usable.covers(footprint):
            continue
        if any(footprint.buffer(0.025, join_style=2).intersects(item) for item in occupied):
            continue
        return round(x, 3), round(y, 3)
    return None


def _assign_hanging_pot(
    placements: list[dict[str, Any]],
    crop_by_slug: dict[str, dict[str, Any]],
    usable: Polygon,
    vertical_allowed: bool,
    plot_area: float,
) -> dict[str, Any] | None:
    if not vertical_allowed or plot_area > 4:
        return None

    eligible: list[dict[str, Any]] = []
    for placement in placements:
        if placement.get("structure_type") != "pot":
            continue
        crop = crop_by_slug.get(str(placement.get("slug")))
        if not crop or crop.get("slug") not in HANGING_POT_PRIORITY:
            continue
        parameters = crop.get("parameters", {})
        spec = placement.get("container_spec") or {}
        if not parameters.get("tiered_rack_eligible"):
            continue
        if float(parameters.get("mature_height_cm", 999)) > 40:
            continue
        if float(spec.get("recommended_depth_cm") or 999) > 25:
            continue
        if float(spec.get("recommended_diameter_cm") or 999) > 30:
            continue
        if parameters.get("trellis_requirement") == "required":
            continue
        centre = _placement_box(placement).centroid
        edge_distance = usable.exterior.distance(centre)
        eligible.append(
            {
                "placement": placement,
                "priority": HANGING_POT_PRIORITY[crop["slug"]],
                "edge_distance": edge_distance,
            }
        )

    if not eligible:
        return None
    selected = sorted(eligible, key=lambda item: (item["priority"], item["edge_distance"], item["placement"]["placement_id"]))[0]["placement"]
    selected["structure_type"] = "hanging_pot"
    selected["zone"] = "vertical_edge"
    spec = selected.get("container_spec") or {}
    return {
        "type": "hanging_pot",
        "placement_id": selected["placement_id"],
        "crop_slug": selected["slug"],
        "name_en": selected["name_en"],
        "name_id": selected["name_id"],
        "x_m": selected["x_m"],
        "y_m": selected["y_m"],
        "width_m": selected["width_m"],
        "recommended_diameter_cm": spec.get("recommended_diameter_cm"),
        "recommended_depth_cm": spec.get("recommended_depth_cm"),
        "support_warning": "Use a load-rated hook and keep the pot clear of the access path.",
    }


def _rack_candidate_key(placement: dict[str, Any], crop: dict[str, Any]) -> tuple:
    spec = placement.get("container_spec") or {}
    parameters = crop.get("parameters", {})
    return (
        float(spec.get("recommended_depth_cm") or 999),
        float(spec.get("recommended_diameter_cm") or 999),
        float(parameters.get("mature_height_cm") or 999),
        str(placement.get("slug")),
        str(placement.get("placement_id")),
    )


def _choose_distinct(
    candidates: list[tuple[dict[str, Any], dict[str, Any]]],
    used_slugs: set[str],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    distinct = [item for item in candidates if str(item[0].get("slug")) not in used_slugs]
    pool = distinct or candidates
    return pool[0] if pool else None


def _assign_tiered_rack(
    placements: list[dict[str, Any]],
    crop_by_slug: dict[str, dict[str, Any]],
    usable: Polygon,
    tiered_rack_allowed: bool,
    sun_direction: str,
) -> dict[str, Any] | None:
    if not tiered_rack_allowed or usable.area < 0.75:
        return None

    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for placement in placements:
        if placement.get("structure_type") != "pot":
            continue
        crop = crop_by_slug.get(str(placement.get("slug")))
        if not crop:
            continue
        parameters = crop.get("parameters", {})
        if not parameters.get("tiered_rack_eligible"):
            continue
        if not parameters.get("permitted_vertical_tiers"):
            continue
        # A household rack should carry compact crops. Tall crops such as
        # kenikir remain on the ground even when the source metadata marks
        # them as generally rack-compatible.
        if float(parameters.get("mature_height_cm") or 999) > 50:
            continue
        candidates.append((placement, crop))

    if not candidates:
        return None

    # Tier 1 can carry the deepest/heaviest eligible pot. Upper tiers only use
    # light, shallow, compact crops to prevent the rack from becoming a generic
    # vertical-placement shortcut.
    tier1_pool = [item for item in candidates if 1 in item[1]["parameters"].get("permitted_vertical_tiers", [])]
    tier1_pool.sort(key=lambda item: _rack_candidate_key(item[0], item[1]), reverse=True)
    tier1 = tier1_pool[0] if tier1_pool else None
    if not tier1:
        return None

    selected: list[tuple[int, dict[str, Any], dict[str, Any]]] = [(1, tier1[0], tier1[1])]
    used_ids = {str(tier1[0]["placement_id"])}
    used_slugs = {str(tier1[0]["slug"])}

    for tier in (2, 3):
        upper = []
        for placement, crop in candidates:
            if str(placement["placement_id"]) in used_ids:
                continue
            parameters = crop.get("parameters", {})
            spec = placement.get("container_spec") or {}
            if tier not in parameters.get("permitted_vertical_tiers", []):
                continue
            if float(spec.get("recommended_depth_cm") or 999) > 25:
                continue
            if float(spec.get("recommended_diameter_cm") or 999) > 30:
                continue
            if float(parameters.get("mature_height_cm") or 999) > 40:
                continue
            if parameters.get("trellis_requirement") == "required":
                continue
            upper.append((placement, crop))
        upper.sort(key=lambda item: _rack_candidate_key(item[0], item[1]))
        chosen = _choose_distinct(upper, used_slugs)
        if chosen:
            selected.append((tier, chosen[0], chosen[1]))
            used_ids.add(str(chosen[0]["placement_id"]))
            used_slugs.add(str(chosen[0]["slug"]))

    if not selected:
        return None

    max_diameter_m = max(
        float((placement.get("container_spec") or {}).get("recommended_diameter_cm") or 25) / 100
        for _, placement, _ in selected
    )
    rack_width = round(min(0.9, max(0.55, max_diameter_m + 0.18)), 2)
    rack_depth = round(min(0.55, max(0.35, max_diameter_m + 0.06)), 2)
    selected_ids = {str(placement["placement_id"]) for _, placement, _ in selected}
    occupied = [
        _placement_box(placement).buffer(0.025, join_style=2)
        for placement in placements
        if str(placement["placement_id"]) not in selected_ids
    ]
    position = _find_module_position(usable, rack_width, rack_depth, occupied, sun_direction)
    if not position:
        return None

    rack_x, rack_y = position
    assignments = []
    for tier, placement, crop in selected:
        placement["structure_type"] = "rack_pot"
        placement["tier"] = tier
        placement["zone"] = "tiered_rack"
        placement["x_m"] = rack_x
        placement["y_m"] = rack_y
        assignments.append(
            {
                "tier": tier,
                "placement_id": placement["placement_id"],
                "crop_slug": placement["slug"],
                "name_en": placement["name_en"],
                "name_id": placement["name_id"],
                "container_depth_cm": (placement.get("container_spec") or {}).get("recommended_depth_cm")
                or crop.get("parameters", {}).get("minimum_container_depth_cm"),
                "container_diameter_cm": (placement.get("container_spec") or {}).get("recommended_diameter_cm")
                or crop.get("parameters", {}).get("minimum_container_diameter_cm"),
            }
        )

    return {
        "type": "tiered_rack",
        "x_m": rack_x,
        "y_m": rack_y,
        "module_width_m": rack_width,
        "module_depth_m": rack_depth,
        "module_height_m": 1.35,
        "tiers": 3,
        "assignments": assignments,
        "warning": "Keep deep or heavy containers on Tier 1; confirm rack load rating and drainage.",
    }


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
    placements: list[dict[str, Any]] = []
    adjustments = []
    vertical_modules: list[dict[str, Any]] = []

    crops = sorted(
        crop_allocations,
        key=lambda crop: (-float(crop["parameters"].get("mature_height_cm", 0)), crop["slug"]),
    )
    crop_by_slug = {str(crop["slug"]): crop for crop in crops}

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
            placement_id = f"{crop['slug']}-{count}"
            placements.append(
                {
                    "placement_id": placement_id,
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
                        "placement_id": placement_id,
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

    hanging = _assign_hanging_pot(placements, crop_by_slug, usable, vertical_allowed, poly.area)
    if hanging:
        vertical_modules.append(hanging)

    rack = _assign_tiered_rack(
        placements,
        crop_by_slug,
        usable,
        tiered_rack_allowed,
        sun_direction,
    )
    if rack:
        vertical_modules.append(rack)

    used_for_compost = [
        _placement_box(placement)
        for placement in placements
        if placement.get("structure_type") != "rack_pot"
    ]
    if rack:
        used_for_compost.append(
            box(
                rack["x_m"],
                rack["y_m"],
                rack["x_m"] + rack["module_width_m"],
                rack["y_m"] + rack["module_depth_m"],
            )
        )

    compost = None
    if poly.area >= 8:
        _, miny, maxx, _ = usable.bounds
        size = 0.45
        candidate = box(maxx - size, miny, maxx, miny + size)
        if usable.covers(candidate) and not any(candidate.intersects(used) for used in used_for_compost):
            compost = {
                "x_m": round(maxx - size, 3),
                "y_m": round(miny, 3),
                "width_m": size,
                "height_m": size,
                "type": "compact_compost_point",
            }

    non_rack_area = sum(
        float(p["width_m"]) * float(p["height_m"])
        for p in placements
        if p.get("structure_type") != "rack_pot"
    )
    rack_area = (
        float(rack["module_width_m"]) * float(rack["module_depth_m"])
        if rack
        else 0.0
    )
    total_area = round(non_rack_area + rack_area, 2)
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
