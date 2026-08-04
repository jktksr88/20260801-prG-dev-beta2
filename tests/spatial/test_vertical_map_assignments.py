from shapely.geometry import box

from app.spatial.layout import generate_layout


def crop(slug, height=30, depth=20, diameter=24, quantity=2, rack=True, tiers=None):
    return {
        "id": f"{slug}-id",
        "slug": slug,
        "name_en": slug.title(),
        "name_id": slug.title(),
        "category": "leafy",
        "target_quantity": quantity,
        "surface": "container",
        "container_spec": {
            "recommended_diameter_cm": diameter,
            "recommended_depth_cm": depth,
            "recommended_volume_l": 8,
        },
        "parameters": {
            "preferred_spacing_cm": diameter,
            "mature_height_cm": height,
            "tiered_rack_eligible": rack,
            "permitted_vertical_tiers": tiers or [1, 2, 3],
            "trellis_requirement": "none",
        },
    }


def test_rack_assignments_reference_real_placements_and_show_tiers():
    layout = generate_layout(
        box(0, 0, 2.5, 1.8),
        [crop("kangkung"), crop("selada"), crop("caisim")],
        vertical_allowed=False,
        tiered_rack_allowed=True,
    )
    rack = next(module for module in layout["vertical_modules"] if module["type"] == "tiered_rack")
    assert rack["assignments"]
    placement_by_id = {item["placement_id"]: item for item in layout["placements"]}
    for assignment in rack["assignments"]:
        placement = placement_by_id[assignment["placement_id"]]
        assert placement["structure_type"] == "rack_pot"
        assert placement["tier"] == assignment["tier"]
        assert placement["slug"] == assignment["crop_slug"]


def test_caisim_is_not_silently_selected_for_hanging_pot():
    layout = generate_layout(
        box(0, 0, 2, 1.5),
        [crop("caisim", quantity=3)],
        vertical_allowed=True,
        tiered_rack_allowed=False,
    )
    assert not any(item["structure_type"] == "hanging_pot" for item in layout["placements"])


def test_hanging_pot_uses_curated_eligible_crop_and_never_duplicates_quantity():
    layout = generate_layout(
        box(0, 0, 2, 1.5),
        [crop("kangkung", quantity=3)],
        vertical_allowed=True,
        tiered_rack_allowed=False,
    )
    hanging = [item for item in layout["placements"] if item["structure_type"] == "hanging_pot"]
    assert len(hanging) == 1
    assert hanging[0]["slug"] == "kangkung"
    assert len(layout["placements"]) == 3
