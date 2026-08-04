from shapely.geometry import box

from app.spatial.layout import generate_layout


def eligible_crop():
    return {
        "id": "caisim-id",
        "slug": "kangkung",
        "name_en": "Water spinach",
        "name_id": "Kangkung",
        "category": "leafy",
        "target_quantity": 3,
        "surface": "container",
        "container_spec": {
            "recommended_diameter_cm": 25,
            "recommended_depth_cm": 20,
            "recommended_volume_l": 8,
        },
        "parameters": {
            "preferred_spacing_cm": 25,
            "mature_height_cm": 30,
            "tiered_rack_eligible": True,
            "permitted_vertical_tiers": [1, 2, 3],
            "trellis_requirement": "none",
        },
    }


def test_hanging_module_references_one_real_crop_placement():
    layout = generate_layout(box(0, 0, 2, 1.5), [eligible_crop()], vertical_allowed=True)
    hanging_placements = [p for p in layout["placements"] if p["structure_type"] == "hanging_pot"]
    hanging_modules = [m for m in layout["vertical_modules"] if m["type"] == "hanging_pot"]
    assert len(hanging_placements) == 1
    assert len(hanging_modules) == 1
    assert hanging_modules[0]["placement_id"] == hanging_placements[0]["placement_id"]
    assert hanging_modules[0]["crop_slug"] == hanging_placements[0]["slug"]
    assert len(layout["placements"]) == 3


def test_no_hanging_legend_data_without_real_placement():
    layout = generate_layout(box(0, 0, 2, 1.5), [eligible_crop()], vertical_allowed=False)
    assert not any(p["structure_type"] == "hanging_pot" for p in layout["placements"])
    assert not any(m["type"] == "hanging_pot" for m in layout["vertical_modules"])
