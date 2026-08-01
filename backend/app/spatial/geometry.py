from __future__ import annotations
from shapely.geometry import Polygon, box
from shapely.validation import explain_validity
from app.schemas.planner import PlotInput

class GeometryError(ValueError):
    pass

def build_polygon(plot: PlotInput) -> Polygon:
    if plot.shape in {"rectangle", "square"}:
        length = float(plot.length_m or 0); width = float(plot.width_m or 0)
        if length <= 0 or width <= 0: raise GeometryError("Length and width must be positive")
        poly = box(0, 0, length, width)
    elif plot.shape == "l_shape":
        length = float(plot.length_m or 0); width = float(plot.width_m or 0)
        if length <= 0 or width <= 0: raise GeometryError("Length and width must be positive")
        cut_x, cut_y = length * 0.52, width * 0.52
        poly = Polygon([(0,0),(length,0),(length,cut_y),(cut_x,cut_y),(cut_x,width),(0,width)])
    else:
        poly = Polygon(plot.points or [])
    if not poly.is_valid:
        raise GeometryError(f"Invalid plot geometry: {explain_validity(poly)}")
    if poly.area <= 0.04:
        raise GeometryError("Plot is too small to calculate a credible plan")
    return poly

def polygon_payload(poly: Polygon) -> list[list[float]]:
    return [[round(float(x),3),round(float(y),3)] for x,y in list(poly.exterior.coords)]

def reserve_access_zone(poly: Polygon, entrance_edge: int | None) -> tuple[Polygon, Polygon | None]:
    minx,miny,maxx,maxy = poly.bounds
    if poly.area < 3.0:
        return poly, None
    depth = min(0.55, max(0.35, min(maxx-minx,maxy-miny)*0.13))
    edge = entrance_edge if entrance_edge is not None else 0
    zones = [box(minx,miny,maxx,miny+depth),box(maxx-depth,miny,maxx,maxy),box(minx,maxy-depth,maxx,maxy),box(minx,miny,minx+depth,maxy)]
    access = poly.intersection(zones[edge%4])
    usable = poly.difference(access.buffer(0.02))
    if usable.is_empty or usable.area < poly.area*0.45:
        return poly, None
    if usable.geom_type == "MultiPolygon":
        usable = max(usable.geoms, key=lambda g:g.area)
    return usable, access
