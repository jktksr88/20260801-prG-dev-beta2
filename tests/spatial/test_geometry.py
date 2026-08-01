import pytest
from shapely.geometry import Polygon, box
from app.schemas.planner import PlotInput
from app.spatial.geometry import build_polygon, GeometryError
from app.spatial.layout import generate_layout

def test_l_shape_uses_actual_polygon():
    poly=build_polygon(PlotInput(shape="l_shape",length_m=3,width_m=2))
    assert round(poly.area,2)<6
    assert poly.is_valid

def test_invalid_custom_polygon_rejected():
    with pytest.raises(GeometryError): build_polygon(PlotInput(shape="custom",points=[(0,0),(2,2),(0,2),(2,0)]))

def test_placements_stay_inside_and_do_not_overlap():
    poly=box(0,0,2,1.5)
    crops=[{"id":"1","slug":"a","name_en":"A","name_id":"A","surface":"container","target_quantity":4,"parameters":{"preferred_spacing_cm":30,"mature_height_cm":30,"trellis_requirement":"none"}},{"id":"2","slug":"b","name_en":"B","name_id":"B","surface":"container","target_quantity":3,"parameters":{"preferred_spacing_cm":40,"mature_height_cm":80,"trellis_requirement":"none"}}]
    result=generate_layout(poly,crops)
    shapes=[]
    for p in result["placements"]:
        s=box(p["x_m"],p["y_m"],p["x_m"]+p["width_m"],p["y_m"]+p["height_m"])
        assert poly.covers(s)
        assert not any(s.intersects(other.buffer(.024)) for other in shapes)
        shapes.append(s)
