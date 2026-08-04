def register(client,email):
    r=client.post("/api/v1/auth/register",json={"email":email,"password":"strong-password-123","preferred_language":"en"})
    assert r.status_code==201,r.text
    return r.json()

def test_health_and_catalog(client):
    assert client.get("/api/v1/health").status_code==200
    data=client.get("/api/v1/plants?page_size=50").json()
    assert data["total"]==50 and len(data["items"])==50

def test_anonymous_planner_journey(client):
    payload={"location":{"city":"Jakarta"},"plot":{"shape":"rectangle","length_m":2,"width_m":1.5,"sun_direction":"north"},"surface":"containers","sunlight":"partial","care_commitment":"regular","primary_goal":"kitchen","desired_crops":[],"excluded_crops":[],"vertical_allowed":True,"tiered_rack_allowed":False,"water_access":"normal","child_or_pet_concerns":False,"language":"en"}
    r=client.post("/api/v1/planner/recommendations",json=payload)
    assert r.status_code==200,r.text
    assert len(r.json()["plans"])==3

def test_plan_ownership_and_public_share(client):
    one=register(client,"owner@example.com");two=register(client,"other@example.com")
    payload={"name":"Balcony","language":"en","planner_input":{"x":1},"plan_data":{"name_en":"Easy Start","crops":[]},"is_public":True}
    saved=client.post("/api/v1/plans",json=payload,headers={"Authorization":f"Bearer {one['access_token']}"})
    assert saved.status_code==201,saved.text
    plan=saved.json()
    assert client.get(f"/api/v1/plans/{plan['id']}",headers={"Authorization":f"Bearer {two['access_token']}"}).status_code==404
    assert client.get(f"/api/v1/public/plans/{plan['share_slug']}").status_code==200

def test_diary_persists_with_deterministic_fallback(client):
    tok=register(client,"diary@example.com")
    headers={"Authorization":f"Bearer {tok['access_token']}"}
    saved=client.post("/api/v1/plans",json={"name":"Diary garden","language":"en","planner_input":{},"plan_data":{"environment":{"seven_day_rain_mm":60},"crops":[{"id":"caisim-test","slug":"caisim","name_en":"Choy sum","name_id":"Caisim / sawi hijau","scientific_name":"Brassica rapa, Parachinensis Group"}]},"is_public":False},headers=headers).json()
    r=client.post("/api/v1/diary",json={"plan_id":saved["id"],"entry_text":"My choy sum leaves are yellow and the soil is wet","user_question":"What should I check?","language":"en"},headers=headers)
    assert r.status_code==201,r.text
    assert r.json()["ai_response"] and "definitive diagnosis" in r.json()["ai_response"]
