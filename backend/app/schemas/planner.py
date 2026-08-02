from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, model_validator

Point = tuple[float, float]

class LocationInput(BaseModel):
    city: str = "Jakarta"
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None

class PlotInput(BaseModel):
    shape: Literal["rectangle", "square", "l_shape", "custom"] = "rectangle"
    length_m: float | None = Field(default=2.0, gt=0, le=100)
    width_m: float | None = Field(default=1.5, gt=0, le=100)
    points: list[Point] | None = None
    entrance_edge: int | None = None
    sun_direction: Literal["north", "east", "south", "west"] = "north"

    @model_validator(mode="after")
    def validate_shape(self):
        if self.shape == "custom" and (not self.points or len(self.points) < 3):
            raise ValueError("Custom polygon requires at least three points")
        return self

class PlannerInput(BaseModel):
    location: LocationInput = LocationInput()
    plot: PlotInput = PlotInput()
    surface: Literal["soil", "containers", "mixed"] = "containers"
    sunlight: Literal["shade", "partial", "full"] = "partial"
    care_commitment: Literal["low", "regular", "hands_on"] = "regular"
    primary_goal: Literal["easy", "fast", "kitchen", "variety", "yield"] = "kitchen"
    desired_crops: list[str] = []
    excluded_crops: list[str] = []
    vertical_allowed: bool = True
    tiered_rack_allowed: bool = False
    water_access: Literal["limited", "normal", "easy"] = "normal"
    household_size: int | None = Field(default=None, ge=1, le=20)
    child_or_pet_concerns: bool = False
    desired_quantity: int | None = Field(default=None, ge=1, le=200)
    container_depth_cm: float | None = Field(default=None, ge=5, le=120)
    language: Literal["en", "id"] = "en"

class SavePlanRequest(BaseModel):
    name: str = Field(default="My GROE Garden", min_length=1, max_length=160)
    language: Literal["en", "id"] = "en"
    planner_input: dict
    plan_data: dict
    is_public: bool = False
