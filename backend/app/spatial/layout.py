from __future__ import annotations
from typing import Any
import math
from shapely.geometry import box, Point, Polygon
from shapely.affinity import translate
from app.spatial.geometry import reserve_access_zone, polygon_payload


def _scan_coordinates(poly: Polygon, step: float, direction: str):
    minx,miny,maxx,maxy=poly.bounds
    xs=[]; x=minx
    while x<=maxx+1e-9: xs.append(round(x,4)); x+=step
    ys=[]; y=miny
    while y<=maxy+1e-9: ys.append(round(y,4)); y+=step
    if direction=="north": ys=list(reversed(ys))
    elif direction=="east": xs=list(reversed(xs))
    elif direction=="south": pass
    elif direction=="west": pass
    for yy in ys:
        row_xs=xs if int((yy-miny)/step)%2==0 else list(reversed(xs))
        for xx in row_xs: yield xx,yy


def generate_layout(poly: Polygon, crop_allocations: list[dict[str,Any]], sun_direction: str="north", entrance_edge: int|None=None, vertical_allowed: bool=True, tiered_rack_allowed: bool=False) -> dict:
    usable, access=reserve_access_zone(poly,entrance_edge)
    used=[]; placements=[]; adjustments=[]; vertical_modules=[]
    # Put taller crops toward the strongest-sun edge first, then compact crops.
    crops=sorted(crop_allocations,key=lambda c:(-float(c["parameters"].get("mature_height_cm",0)),c["slug"]))
    for crop in crops:
        p=crop["parameters"]
        target=max(1,int(crop.get("target_quantity",1)))
        spacing=max(0.10,float(p.get("preferred_spacing_cm",25))/100)
        trellised=p.get("trellis_requirement")=="required" and vertical_allowed
        width=spacing
        depth=min(spacing,0.42) if trellised else spacing
        count=0
        for x,y in _scan_coordinates(usable,max(0.06,min(width,depth)/3),sun_direction):
            shape=box(x,y,x+width,y+depth)
            if not usable.covers(shape): continue
            if any(shape.intersects(u.buffer(0.025)) for u in used): continue
            used.append(shape); count+=1
            placements.append({
                "placement_id":f"{crop['slug']}-{count}","crop_profile_id":crop["id"],"slug":crop["slug"],
                "name_en":crop["name_en"],"name_id":crop["name_id"],"x_m":round(x,3),"y_m":round(y,3),
                "width_m":round(width,3),"height_m":round(depth,3),"shape":"container" if crop.get("surface")!="soil" else "soil",
                "trellis":trellised,"tier":None,"zone":"main","spacing_m":round(spacing,3)
            })
            if trellised:
                vertical_modules.append({"type":"trellis","crop_slug":crop["slug"],"x_m":round(x,3),"y_m":round(y,3),"width_m":round(width,3),"height_m":round(float(p.get("mature_height_cm",150))/100,2),"support_strength":p.get("support_strength","strong")})
            if count>=target: break
        if count<target:
            adjustments.append({"code":"QUANTITY_REDUCED_TO_FIT","crop_slug":crop["slug"],"requested":target,"feasible":count})
    # Optional rack is represented separately and only uses shallow eligible crops.
    if tiered_rack_allowed:
        eligible=[c for c in crops if c["parameters"].get("tiered_rack_eligible") and 2 in c["parameters"].get("permitted_vertical_tiers",[])]
        if eligible and poly.area>=0.75:
            rack_width=min(0.8,max(0.5,math.sqrt(poly.area)*0.35))
            assignments=[]
            for tier,c in zip([1,2,3],eligible[:3]):
                if tier in c["parameters"].get("permitted_vertical_tiers",[]):
                    assignments.append({"tier":tier,"crop_slug":c["slug"],"container_depth_cm":c["parameters"].get("minimum_container_depth_cm")})
            if assignments:
                vertical_modules.append({"type":"tiered_rack","module_width_m":round(rack_width,2),"module_height_m":1.35,"tiers":3,"assignments":assignments,"warning":"Keep deep or heavy containers on Tier 1; confirm rack load rating and drainage."})
    compost=None
    if poly.area>=8:
        minx,miny,maxx,maxy=usable.bounds
        size=0.45; candidate=box(maxx-size,miny,maxx,miny+size)
        if usable.covers(candidate) and not any(candidate.intersects(u.buffer(0.03)) for u in used):
            compost={"x_m":round(maxx-size,3),"y_m":round(miny,3),"width_m":size,"height_m":size,"type":"compact_compost_point"}
    total_area=round(sum(p["width_m"]*p["height_m"] for p in placements),2)
    return {"plot_boundary":polygon_payload(poly),"usable_boundary":polygon_payload(usable),"plot_area_m2":round(poly.area,2),"usable_area_m2":round(usable.area,2),"access_zone":polygon_payload(access) if access and not access.is_empty else None,"placements":placements,"vertical_modules":vertical_modules,"compost":compost,"occupied_area_m2":total_area,"adjustments":adjustments,"scale_unit":"metres","sun_direction":sun_direction}
