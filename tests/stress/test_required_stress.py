import os
import pytest
import asyncio
from shapely.geometry import Polygon, box
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models import CropProfile
from app.schemas.planner import PlannerInput, PlotInput, LocationInput
from app.planning.optimizer import generate_recommendations, crop_to_dict
from app.planning.scoring import score_crop
from app.spatial.geometry import build_polygon, GeometryError
from app.spatial.layout import generate_layout
from app.weather.client import get_weather_context
from app.ai.fallback import get_ai_service


def slugs(plan):
    return {c["slug"] for c in plan["crops"]}


def test_A_tiny_container_balcony(db):
    req=PlannerInput(location=LocationInput(city="Jakarta"),plot=PlotInput(length_m=1,width_m=1),surface="containers",sunlight="full",care_commitment="low",primary_goal="variety",vertical_allowed=True)
    out=generate_recommendations(db,req,{"mean_temperature_c":29})
    assert len(out["plans"])==3
    assert all(p["total_plants"]>=1 for p in out["plans"])
    assert all(not {"labu-kuning","semangka","pepaya-kerdil"}.intersection(slugs(p)) for p in out["plans"])


def test_B_narrow_partial_sun_porch_and_tiers(db):
    req=PlannerInput(plot=PlotInput(length_m=2,width_m=.6),surface="containers",sunlight="partial",care_commitment="regular",primary_goal="kitchen",vertical_allowed=True,tiered_rack_allowed=True)
    out=generate_recommendations(db,req,{"mean_temperature_c":28})
    assert len(out["plans"])==3
    for p in out["plans"]:
        for placement in p["layout"]["placements"]:
            assert placement["x_m"]>=0 and placement["y_m"]>=0
        for module in p["layout"]["vertical_modules"]:
            if module.get("type")=="tiered_rack":
                upper={a["crop_slug"] for a in module.get("assignments",[]) if a["tier"]>1}
                assert not upper.intersection({"bit","wortel","lobak-putih","kentang"})


def test_C_direct_soil_family_garden_has_access(db):
    req=PlannerInput(location=LocationInput(city="Jakarta"),plot=PlotInput(length_m=4,width_m=3,entrance_edge=0,sun_direction="north"),surface="soil",sunlight="full",care_commitment="regular",primary_goal="kitchen")
    out=generate_recommendations(db,req,{"mean_temperature_c":28})
    assert all(p["layout"]["access_zone"] for p in out["plans"])
    assert all(p["total_plants"]>0 for p in out["plans"])


def test_D_cooler_highland_improves_sensitive_crop(db):
    crop=db.scalar(select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.slug=="kale"))
    req=PlannerInput(plot=PlotInput(length_m=3,width_m=2),surface="mixed",sunlight="full",care_commitment="hands_on")
    cool=score_crop(crop_to_dict(crop),req,6,{"mean_temperature_c":23})
    hot=score_crop(crop_to_dict(crop),req,6,{"mean_temperature_c":31})
    assert cool.score>hot.score


def test_E_hot_lowland_penalizes_sensitive_profiles(db):
    req=PlannerInput(location=LocationInput(city="Surabaya"),plot=PlotInput(length_m=3,width_m=2),surface="containers",sunlight="full")
    out=generate_recommendations(db,req,{"mean_temperature_c":31})
    scores={c["slug"]:c["score"] for p in out["plans"] for c in p["crops"]}
    assert all(scores.get(s,0)<80 for s in {"stroberi","kale","kubis","paprika","kentang"} if s in scores)


def test_F_impossible_large_crop_request_has_substitutes(db):
    req=PlannerInput(plot=PlotInput(length_m=1,width_m=.5),surface="containers",vertical_allowed=False,desired_crops=["labu-kuning","semangka","pepaya-kerdil"])
    out=generate_recommendations(db,req,{"mean_temperature_c":29})
    assert out["requested_crop_review"]
    assert all(x["alternatives"] for x in out["requested_crop_review"])


def test_G_shallow_container_root_test(db):
    for slug in ["bit","wortel","lobak-putih"]:
        crop=db.scalar(select(CropProfile).options(selectinload(CropProfile.species)).where(CropProfile.slug==slug))
        result=score_crop(crop_to_dict(crop),PlannerInput(surface="containers",container_depth_cm=15),1,{"mean_temperature_c":26})
        assert "CONTAINER_TOO_SHALLOW" in result.hard_constraints


def test_H_vertical_tier_integrity():
    poly=box(0,0,2,1)
    crops=[
      {"id":"leaf","slug":"pakcoy","name_en":"Pak choi","name_id":"Pakcoy","surface":"container","target_quantity":1,"parameters":{"preferred_spacing_cm":22,"mature_height_cm":25,"trellis_requirement":"none","tiered_rack_eligible":True,"permitted_vertical_tiers":[1,2,3],"minimum_container_depth_cm":18}},
      {"id":"root","slug":"bit","name_en":"Beetroot","name_id":"Bit","surface":"container","target_quantity":1,"parameters":{"preferred_spacing_cm":20,"mature_height_cm":30,"trellis_requirement":"none","tiered_rack_eligible":False,"permitted_vertical_tiers":[1],"minimum_container_depth_cm":30}},
    ]
    layout=generate_layout(poly,crops,tiered_rack_allowed=True)
    racks=[m for m in layout["vertical_modules"] if m.get("type")=="tiered_rack"]
    assert racks
    upper={a["crop_slug"] for r in racks for a in r["assignments"] if a["tier"]>1}
    assert "bit" not in upper


def test_I_l_shape_uses_both_valid_arms(db):
    req=PlannerInput(plot=PlotInput(shape="l_shape",length_m=3,width_m=2,entrance_edge=0),surface="containers",sunlight="partial")
    out=generate_recommendations(db,req,{"mean_temperature_c":27})
    poly=build_polygon(req.plot)
    assert round(poly.area,2)==round(3*2-(3*.48)*(2*.48),2)
    for p in out["plans"]:
        for x in p["layout"]["placements"]:
            assert poly.covers(box(x["x_m"],x["y_m"],x["x_m"]+x["width_m"],x["y_m"]+x["height_m"]))


def test_J_invalid_custom_polygon_preserves_validation_boundary():
    with pytest.raises(GeometryError):
        build_polygon(PlotInput(shape="custom",points=[(0,0),(2,2),(0,2),(2,0)]))


def test_K_no_ai_key_has_controlled_fallback():
    os.environ.pop("AI_API_KEY",None)
    service=get_ai_service()
    assert asyncio.run(service.explain_diary({},"yellow leaves","en")) is None


def test_L_weather_provider_failure_uses_reduced_confidence():
    result=asyncio.run(get_weather_context("Jakarta",None,None,None))
    assert result["provider_available"] is False
    assert result["confidence"] in {"fallback","reduced"}


def test_M_bilingual_consistency(db):
    rows=db.scalars(select(CropProfile)).all()
    assert len(rows)==50
    assert all(r.name_en and r.name_id and r.guidance_en and r.guidance_id for r in rows)
    assert all(r.species.scientific_name for r in rows)


def test_N_database_completeness_and_ids(db):
    rows=db.scalars(select(CropProfile)).all()
    assert len(rows)==50
    assert len({r.id for r in rows})==50
    assert all(r.fields_requiring_review for r in rows)


def test_O_plan_distinction(db):
    out=generate_recommendations(db,PlannerInput(plot=PlotInput(length_m=4,width_m=3),surface="soil",sunlight="full"),{"mean_temperature_c":28})
    sets=[slugs(p) for p in out["plans"]]
    assert len({tuple(sorted(x)) for x in sets})==3
    for i in range(3):
        for j in range(i+1,3):
            assert len(sets[i]&sets[j])/max(1,len(sets[i]|sets[j]))<.76


def test_P_plot_capacity_and_no_overlap(db):
    out=generate_recommendations(db,PlannerInput(plot=PlotInput(length_m=1.2,width_m=.8),surface="containers",desired_quantity=100),{"mean_temperature_c":28})
    for plan in out["plans"]:
        shapes=[]
        poly=Polygon(plan["layout"]["plot_boundary"])
        for p in plan["layout"]["placements"]:
            shape=box(p["x_m"],p["y_m"],p["x_m"]+p["width_m"],p["y_m"]+p["height_m"])
            assert poly.covers(shape)
            assert not any(shape.intersects(s.buffer(.024)) for s in shapes)
            shapes.append(shape)
        assert any(a["code"]=="QUANTITY_REDUCED_TO_FIT" for a in plan["layout"]["adjustments"])


def test_Q_compost_space_logic():
    crop={"id":"1","slug":"pakcoy","name_en":"Pak choi","name_id":"Pakcoy","surface":"container","target_quantity":1,"parameters":{"preferred_spacing_cm":22,"mature_height_cm":25,"trellis_requirement":"none"}}
    small=generate_layout(box(0,0,1,.6),[crop])
    large=generate_layout(box(0,0,4,3),[crop])
    assert small["compost"] is None
    assert large["compost"] is not None


def test_R_anonymous_save_blocked(client):
    r=client.post("/api/v1/plans",json={"name":"x","language":"en","planner_input":{},"plan_data":{},"is_public":False})
    assert r.status_code==401
