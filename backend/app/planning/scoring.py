from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.schemas.planner import PlannerInput

WEIGHTS = {"climate":0.18,"sun":0.17,"spatial":0.16,"root":0.10,"surface":0.10,"maintenance":0.10,"goal":0.10,"beginner":0.06,"water":0.03}
SUN_HOURS = {"shade":2.0,"partial":4.5,"full":7.0}
CARE_LEVEL = {"low":0,"regular":1,"hands_on":2}
MAINT_LEVEL = {"low":0,"regular":1,"high":2}

@dataclass
class ScoreResult:
    score: int
    classification: str
    reasons: list[str]
    adjustments: list[str]
    hard_constraints: list[str]
    dimensions: dict[str,float]

def _clamp(value: float) -> float:
    return max(0.0,min(100.0,value))

def score_crop(crop: dict[str,Any], request: PlannerInput, usable_area: float, climate: dict[str,Any]) -> ScoreResult:
    p=crop["parameters"]
    hard=[]; reasons=[]; adjustments=[]
    sun=SUN_HOURS[request.sunlight]
    min_sun=float(p.get("minimum_direct_sun_hours",3))
    preferred=float(p.get("preferred_direct_sun_hours",5))
    if sun < min_sun:
        sun_score=max(10,100-(min_sun-sun)*28)
        if p.get("partial_shade_tolerance") and request.sunlight!="shade": sun_score=max(sun_score,62)
        adjustments.append("LIGHT_LIMITED")
    else:
        sun_score=100 if sun>=preferred else 78
        reasons.append("SUN_FIT")
    temp=float(climate.get("mean_temperature_c",28))
    ideal_min=float(p.get("temperature_ideal_min_c",20)); ideal_max=float(p.get("temperature_ideal_max_c",31))
    abs_min=float(p.get("temperature_absolute_min_c",12)); abs_max=float(p.get("temperature_absolute_max_c",37))
    if temp < abs_min or temp > abs_max:
        climate_score=0; hard.append("SEVERE_CLIMATE_INCOMPATIBILITY")
    elif ideal_min <= temp <= ideal_max:
        climate_score=95; reasons.append("CLIMATE_FIT")
    else:
        climate_score=max(35,100-min(abs(temp-ideal_min),abs(temp-ideal_max))*12)
        adjustments.append("CLIMATE_PROTECTION")
    footprint=max(0.01,(float(p["preferred_spacing_cm"])/100)**2)
    spatial_score=_clamp((usable_area/max(footprint,0.01))*34)
    if footprint>usable_area*1.05:
        hard.append("PLANT_FOOTPRINT_CANNOT_FIT")
    elif footprint>usable_area*0.42:
        adjustments.append("REDUCE_QUANTITY")
    depth=request.container_depth_cm
    root_score=100
    if request.surface=="containers":
        if not p.get("container_eligible",True): hard.append("INVALID_SURFACE_TYPE")
        if depth is not None and depth < float(p.get("minimum_container_depth_cm",15)):
            hard.append("CONTAINER_TOO_SHALLOW")
            root_score=0
    elif request.surface=="soil" and not p.get("direct_soil_eligible",True):
        hard.append("INVALID_SURFACE_TYPE")
    surface_score=100
    if p.get("trellis_requirement")=="required" and not request.vertical_allowed:
        hard.append("REQUIRED_SUPPORT_UNAVAILABLE")
    maintenance_gap=MAINT_LEVEL.get(p.get("maintenance_intensity","regular"),1)-CARE_LEVEL[request.care_commitment]
    maintenance_score=100 if maintenance_gap<=0 else max(30,100-maintenance_gap*42)
    if maintenance_gap>0: adjustments.append("CARE_COMMITMENT_STRETCH")
    beginner=float(p.get("beginner_success_rating",60))
    goal=request.primary_goal
    goal_score=60
    days=float(p.get("days_to_first_harvest_min",90))
    if goal=="fast": goal_score=_clamp(120-days)
    elif goal=="easy": goal_score=beginner
    elif goal=="kitchen": goal_score=85 if crop["category"] in {"leafy","herb","root"} else 70
    elif goal=="variety": goal_score=78
    elif goal=="yield": goal_score=82 if p.get("harvest_frequency") in {"weekly","as_needed"} else 58
    water_need=p.get("water_need","medium")
    water_score=100
    if request.water_access=="limited" and water_need=="high": water_score=42; adjustments.append("WATER_ACCESS_LIMITED")
    dims={"climate":climate_score,"sun":sun_score,"spatial":spatial_score,"root":root_score,"surface":surface_score,"maintenance":maintenance_score,"goal":goal_score,"beginner":beginner,"water":water_score}
    score=round(sum(dims[k]*WEIGHTS[k] for k in WEIGHTS))
    if hard: classification="not_suitable"; score=min(score,39)
    elif score>=72: classification="recommended"
    elif score>=45: classification="possible_with_adjustments"
    else: classification="not_suitable"
    if classification=="recommended": reasons.append("STRONG_OVERALL_FIT")
    return ScoreResult(score,classification,sorted(set(reasons)),sorted(set(adjustments)),sorted(set(hard)),{k:round(v,1) for k,v in dims.items()})
