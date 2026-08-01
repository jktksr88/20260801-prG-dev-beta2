from __future__ import annotations
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import CropProfile
from app.schemas.planner import PlannerInput
from app.spatial.geometry import build_polygon, reserve_access_zone, GeometryError
from app.spatial.layout import generate_layout
from app.planning.scoring import score_crop
from app.weather.climate import fallback_climate

PLAN_CONFIGS = [
    {"key":"easy_start","name_en":"Easy Start","name_id":"Mulai Mudah","accent":"groe","proposition_en":"The most forgiving route to a first harvest.","proposition_id":"Jalur paling ramah untuk panen pertama."},
    {"key":"fast_harvest","name_en":"Fast Harvest","name_id":"Panen Cepat","accent":"citrus","proposition_en":"Shorter waits and repeat picking where possible.","proposition_id":"Waktu tunggu lebih singkat dan panen berulang bila memungkinkan."},
    {"key":"balanced_kitchen","name_en":"Balanced Kitchen","name_id":"Dapur Seimbang","accent":"lilac","proposition_en":"A practical mix for everyday cooking.","proposition_id":"Kombinasi praktis untuk kebutuhan masak sehari-hari."},
]

def crop_to_dict(c: CropProfile) -> dict[str,Any]:
    return {"id":c.id,"slug":c.slug,"scientific_name":c.species.scientific_name,"name_en":c.name_en,"name_id":c.name_id,"category":c.category,"annual_or_perennial":c.annual_or_perennial,"parameters":c.parameters,"guidance_en":c.guidance_en,"guidance_id":c.guidance_id,"verification_status":c.verification_status,"confidence_level":c.confidence_level}

def _rank(crop: dict, scored: dict, plan_key: str, request: PlannerInput, previous: list[set[str]]) -> float:
    p=crop["parameters"]; s=float(scored["score"]); days=float(p.get("days_to_first_harvest_min",90)); beginner=float(p.get("beginner_success_rating",60)); width=float(p.get("preferred_spacing_cm",30))
    if plan_key=="easy_start": val=s*1.1+beginner*0.65-days*0.08-width*0.08
    elif plan_key=="fast_harvest": val=s+max(0,125-days)*0.72+(18 if p.get("regrowth_capable") else 0)+(10 if p.get("succession_planting_eligible") else 0)
    else: val=s+({"leafy":18,"herb":16,"root":10,"fruiting":8}.get(crop["category"],0))+beginner*0.18
    if crop["slug"] in request.desired_crops: val+=55
    if any(crop["slug"] in x for x in previous): val-=12*sum(crop["slug"] in x for x in previous)
    return val

def _select_for_plan(candidates: list[dict], score_map: dict[str,dict], config: dict, request: PlannerInput, area: float, previous: list[set[str]]) -> list[dict]:
    target=2 if area<0.7 else 3 if area<1.4 else 4 if area<3 else 5 if area<7 else 6
    ranked=sorted(candidates,key=lambda c:(-_rank(c,score_map[c["slug"]],config["key"],request,previous),c["slug"]))
    selected=[]
    if config["key"]=="balanced_kitchen":
        for category in ["leafy","herb","fruiting","root"]:
            hit=next((c for c in ranked if c["category"]==category and c not in selected),None)
            if hit and len(selected)<target: selected.append(hit)
    for c in ranked:
        if len(selected)>=target: break
        if c not in selected: selected.append(c)
    # Replace crops until overlap is meaningfully below 75% where alternatives exist.
    for prior in previous:
        if selected and len(set(c["slug"] for c in selected)&prior)/len(set(c["slug"] for c in selected)|prior)>=0.75:
            for alt in ranked:
                if alt not in selected and alt["slug"] not in prior:
                    selected[-1]=alt; break
    return selected

def _allocate(selected: list[dict], area: float, plan_key: str, request: PlannerInput) -> list[dict]:
    if not selected: return []
    usable_budget=area*(0.82 if area<3 else 0.72)
    weights=[]
    for c in selected:
        p=c["parameters"]; w=1.0
        if plan_key=="fast_harvest": w+=max(0,90-float(p.get("days_to_first_harvest_min",90)))/90
        if plan_key=="easy_start": w+=float(p.get("beginner_success_rating",60))/120
        if plan_key=="balanced_kitchen" and c["category"] in {"leafy","herb"}: w+=0.3
        weights.append(w)
    total=sum(weights)
    out=[]
    for c,w in zip(selected,weights):
        p=c["parameters"]
        footprint=max(0.025,(float(p.get("preferred_spacing_cm",25))/100)**2)
        qty=max(1,min(8,int((usable_budget*w/total)/footprint)))
        if request.desired_quantity is not None:
            qty=max(1,min(qty,max(1,request.desired_quantity//len(selected))))
        out.append({**c,"target_quantity":qty,"surface":"soil" if request.surface=="soil" else "container"})
    return out

def _explanation(config: dict, request: PlannerInput, layout: dict, crops: list[dict], language: str) -> tuple[str,list[str],str]:
    reduced=[a for a in layout["adjustments"] if a["code"]=="QUANTITY_REDUCED_TO_FIT"]
    if language=="id":
        why=f"Rencana ini menyesuaikan {len(crops)} jenis tanaman dengan ruang {layout['plot_area_m2']} m², kondisi cahaya, dan tingkat perawatan Anda."
        adjustments=[f"Jumlah {a['crop_slug']} dikurangi dari {a['requested']} menjadi {a['feasible']} agar benar-benar muat." for a in reduced]
        if not layout["compost"]: adjustments.append("Kompos tidak dipaksakan ke ruang kecil; gunakan opsi kompak atau kompos komunitas.")
        trade="Lebih banyak variasi biasanya mengurangi jumlah setiap tanaman." if config["key"]=="balanced_kitchen" else ("Panen lebih cepat dapat membatasi pilihan tanaman berumur panjang." if config["key"]=="fast_harvest" else "Pilihan yang lebih mudah mungkin menghasilkan variasi yang lebih sedikit.")
    else:
        why=f"This plan fits {len(crops)} crop profiles into {layout['plot_area_m2']} m² while accounting for light, care commitment and physical capacity."
        adjustments=[f"{a['crop_slug']} was reduced from {a['requested']} to {a['feasible']} so the layout remains buildable." for a in reduced]
        if not layout["compost"]: adjustments.append("A compost bin was not forced into the space; use a compact or community option.")
        trade="More variety usually means fewer plants of each crop." if config["key"]=="balanced_kitchen" else ("Faster harvest timing can exclude longer-cycle crops." if config["key"]=="fast_harvest" else "The most forgiving choices may offer less variety.")
    return why,adjustments,trade

def generate_recommendations(db: Session, request: PlannerInput, climate: dict|None=None) -> dict:
    poly=build_polygon(request.plot)
    usable,_=reserve_access_zone(poly,request.plot.entrance_edge)
    climate=climate or fallback_climate(request.location.city,request.location.elevation_m)
    rows=db.scalars(select(CropProfile).where(CropProfile.active.is_(True)).order_by(CropProfile.slug)).all()
    crops=[crop_to_dict(c) for c in rows]
    score_map={}
    for c in crops:
        r=score_crop(c,request,usable.area,climate)
        score_map[c["slug"]]={"score":r.score,"classification":r.classification,"reason_codes":r.reasons,"adjustment_codes":r.adjustments,"hard_constraints":r.hard_constraints,"dimensions":r.dimensions}
    excluded=set(request.excluded_crops)
    candidates=[c for c in crops if c["slug"] not in excluded and score_map[c["slug"]]["classification"]!="not_suitable"]
    if not candidates:
        # Keep physically possible options even when environmental scores are weak.
        candidates=[c for c in crops if c["slug"] not in excluded and not score_map[c["slug"]]["hard_constraints"]]
    plans=[]; previous=[]
    for config in PLAN_CONFIGS:
        selected=_select_for_plan(candidates,score_map,config,request,usable.area,previous)
        allocations=_allocate(selected,usable.area,config["key"],request)
        layout=generate_layout(poly,allocations,request.plot.sun_direction,request.plot.entrance_edge,request.vertical_allowed,request.tiered_rack_allowed)
        actual_slugs={p["slug"] for p in layout["placements"]}
        final=[c for c in selected if c["slug"] in actual_slugs]
        # If the first packing pass was too restrictive, retain at least the strongest crop in the explanation.
        if not final and selected: final=selected[:1]
        previous.append(set(c["slug"] for c in final))
        crop_summaries=[]
        for c in final:
            count=sum(1 for p in layout["placements"] if p["slug"]==c["slug"])
            crop_summaries.append({"id":c["id"],"slug":c["slug"],"name_en":c["name_en"],"name_id":c["name_id"],"scientific_name":c["scientific_name"],"category":c["category"],"quantity":count,"score":score_map[c["slug"]]["score"],"classification":score_map[c["slug"]]["classification"],"reason_codes":score_map[c["slug"]]["reason_codes"],"adjustment_codes":score_map[c["slug"]]["adjustment_codes"],"hard_constraints":score_map[c["slug"]]["hard_constraints"],"parameters":c["parameters"],"verification_status":c["verification_status"]})
        scores=[x["score"] for x in crop_summaries] or [0]
        first_harvest=min((x["parameters"].get("days_to_first_harvest_min",999) for x in crop_summaries),default=None)
        care=sum(float(x["parameters"].get("estimated_weekly_care_minutes",0))*max(1,x["quantity"]) for x in crop_summaries)
        why,adjustments,trade=_explanation(config,request,layout,crop_summaries,request.language)
        plans.append({**config,"feasibility_score":round(sum(scores)/len(scores)),"beginner_difficulty":"easy" if config["key"]=="easy_start" else "moderate","crop_profile_count":len(crop_summaries),"total_plants":sum(x["quantity"] for x in crop_summaries),"estimated_occupied_area_m2":layout["occupied_area_m2"],"containers_required":sum(x["quantity"] for x in crop_summaries) if request.surface!="soil" else 0,"vertical_modules_required":len(layout["vertical_modules"]),"weekly_care_minutes":round(care),"expected_first_harvest_days":first_harvest,"expected_harvest_pattern":"staggered_and_repeat" if config["key"]=="fast_harvest" else "mixed","why_it_fits":why,"adjustments":adjustments,"trade_off":trade,"crops":crop_summaries,"layout":layout})
    # Report requested crops that are genuinely unsuitable and suggest alternatives.
    requested_review=[]
    for slug in request.desired_crops:
        if slug in score_map and score_map[slug]["classification"]=="not_suitable":
            alternatives=sorted(candidates,key=lambda c:-score_map[c["slug"]]["score"])[:3]
            requested_review.append({"slug":slug,"classification":"not_suitable","hard_constraints":score_map[slug]["hard_constraints"],"alternatives":[a["slug"] for a in alternatives]})
    return {"input_summary":request.model_dump(),"environment":climate,"plot":{"area_m2":round(poly.area,2),"usable_area_m2":round(usable.area,2)},"plans":plans,"requested_crop_review":requested_review,"engine_version":"1.0.0","deterministic":True,"data_version":"initial-50-v1"}
