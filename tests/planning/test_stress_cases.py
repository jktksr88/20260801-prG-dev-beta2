from app.schemas.planner import PlannerInput, PlotInput, LocationInput
from app.planning.optimizer import generate_recommendations

def test_tiny_balcony_returns_three_useful_plans(db):
    request=PlannerInput(location=LocationInput(city="Jakarta"),plot=PlotInput(length_m=1,width_m=1),surface="containers",sunlight="full",care_commitment="low",primary_goal="variety",vertical_allowed=True)
    result=generate_recommendations(db,request,{"mean_temperature_c":29,"confidence":"test"})
    assert len(result["plans"])==3
    assert all(p["crop_profile_count"]>=1 for p in result["plans"])
    banned={"labu-kuning","semangka","pepaya-kerdil"}
    assert all(not banned.intersection({c["slug"] for c in p["crops"]}) for p in result["plans"])

def test_hot_lowland_does_not_treat_sensitive_crops_as_easy(db):
    request=PlannerInput(location=LocationInput(city="Surabaya"),plot=PlotInput(length_m=3,width_m=2),surface="containers",sunlight="full")
    result=generate_recommendations(db,request,{"mean_temperature_c":31,"confidence":"test"})
    sensitive={"stroberi","kale","kubis","paprika","kentang"}
    chosen=[c for p in result["plans"] for c in p["crops"] if c["slug"] in sensitive]
    assert all(c["score"]<80 for c in chosen)

def test_impossible_requested_crops_receive_alternatives(db):
    request=PlannerInput(plot=PlotInput(length_m=1,width_m=.5),surface="containers",vertical_allowed=False,desired_crops=["labu-kuning","semangka","pepaya-kerdil"])
    result=generate_recommendations(db,request,{"mean_temperature_c":29,"confidence":"test"})
    assert result["requested_crop_review"]
    assert len(result["plans"])==3

def test_plan_sets_are_not_near_duplicates_when_alternatives_exist(db):
    request=PlannerInput(plot=PlotInput(length_m=4,width_m=3),surface="soil",sunlight="full",primary_goal="kitchen")
    result=generate_recommendations(db,request,{"mean_temperature_c":28,"confidence":"test"})
    sets=[{c["slug"] for c in p["crops"]} for p in result["plans"]]
    for i in range(3):
        for j in range(i+1,3):
            similarity=len(sets[i]&sets[j])/max(1,len(sets[i]|sets[j]))
            assert similarity<.76
