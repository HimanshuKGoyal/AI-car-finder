# reco_service/app/schemas/ranking.py
from typing import Dict, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator

# Aliases: use camelCase on the wire, Pythonic snake_case in code
def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(s.capitalize() for s in parts[1:])

class AppBaseModel(BaseModel):
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel,
        "str_strip_whitespace": True,
        "use_enum_values": True,  # serialize enums as their values
    }

class Gender(str, Enum):
    male = "male"
    female = "female"

class BodyType(str, Enum):
    hatchbacks = "Hatchbacks"
    entry_level_sedans = "Entry Level Sedans"
    luxury_sedans = "Luxury Sedans"
    suv = "SUV"

class FuelType(str, Enum):
    petrol = "Petrol"
    diesel = "Diesel"
    lpg = "LPG"
    cng = "CNG"
    electric = "Electric"

class FamilySize(str, Enum):
    single = "single"
    married_no_kids = "married_no_kids"
    married_with_kids = "married_with_kids"
    large = "large"

class SpecialNeed(str, Enum):
    big = "big"
    tall = "tall"
    commercial = "commercial"
    chauffeur = "chauffeur"

class Priority(str, Enum):
    cheap_to_run = "cheap_to_run"
    features = "features"
    performance = "performance"
    safety = "safety"
    mileage = "mileage"

class FeaturePriority(str, Enum):
    low_maintenance = "Low Maintenance of the Car"
    passenger_features = "Passenger Features in the Car"
    comfort_features = "Comfort Features for the Car"
    driver_safety = "Safety Features for the Driver"
    driving_convenience = "Convenience of Driving"

class LuggageSize(str, Enum):
    small = "small"
    big = "big"
    none = "none"

class MusicSource(str, Enum):
    cd = "cd"
    radio = "radio"
    ipod = "ipod"
    smartphone = "smartphone"
    usb = "usb"

class ColorPreferenceValue(str, Enum):
    like = "like"
    dislike = "dislike"
    neutral = "neutral"

class PurchaseBasics(AppBaseModel):
    age: int = Field(..., ge=18, le=100)
    gender: Gender
    budget: int = Field(..., ge=100_000, le=5_000_000)  # INR 1L–50L
    body_types: List[BodyType] = Field(..., min_length=1, alias="bodyTypes")
    fuel_types: List[FuelType] = Field(..., min_length=1, alias="fuelTypes")

    @field_validator("body_types", "fuel_types", mode="before")
    @classmethod
    def dedupe_lists(cls, v: List[str], info):
        # Determine the target Enum type from the field's annotation
        field_name = info.field_name
        if field_name == "body_types":
            TargetEnum = BodyType
        elif field_name == "fuel_types":
            TargetEnum = FuelType
        else:
            # This should not happen if validator is correctly applied to these fields
            raise ValueError("Unknown field for dedupe_lists validator")

        seen = set()
        result = []
        for item_str in v:
            # Convert string to enum member explicitly
            try:
                enum_member = TargetEnum(item_str)
                if enum_member not in seen:
                    seen.add(enum_member)
                    result.append(enum_member)
            except ValueError:
                # If string doesn't match an enum value, keep as string or raise error
                # For now, let's assume valid enum values are always passed, or Pydantic's
                # subsequent validation will catch invalid ones.
                # If we want to strictly enforce enum conversion here, we'd raise an error.
                if item_str not in seen:
                    seen.add(item_str)
                    result.append(item_str) # Fallback to string if not a valid enum

        return result

class FamilyTravel(AppBaseModel):
    family_size: FamilySize = Field(..., alias="familySize")
    special_needs: List[SpecialNeed] = Field(default_factory=list, alias="specialNeeds")
    city_driving: int = Field(..., ge=1, le=4, alias="cityDriving")
    highway_driving: int = Field(..., ge=1, le=4, alias="highwayDriving")

    @field_validator("special_needs")
    @classmethod
    def dedupe_special_needs(cls, v: List[str]):
        seen = set()
        result = []
        for item in v:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

class NeedsPriorities(AppBaseModel):
    priorities: List[Priority] = Field(..., min_length=1)
    brand_value: int = Field(..., ge=1, le=4, alias="brandValue")
    looks_intensity: int = Field(..., ge=1, le=4, alias="looksIntensity")
    feature_priority: List[FeaturePriority] = Field(default_factory=list, alias="featurePriority")

    @field_validator("priorities", "feature_priority")
    @classmethod
    def dedupe_priorities(cls, v: List[str]):
        seen = set()
        result = []
        for item in v:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

class OtherPreferences(AppBaseModel):
    luggage_size: LuggageSize = Field(..., alias="luggageSize")
    music_importance: int = Field(..., ge=1, le=10, alias="musicImportance")
    music_source: MusicSource = Field(..., alias="musicSource")
    color_preferences: Dict[str, ColorPreferenceValue] = Field(default_factory=dict, alias="colorPreferences")

    @field_validator("color_preferences")
    @classmethod
    def normalize_color_keys(cls, v: Dict[str, ColorPreferenceValue]):
        # Normalize keys: trim spaces and lowercase. This prevents duplicates like "White" vs " white ".
        normalized: Dict[str, ColorPreferenceValue] = {}
        for k, val in v.items():
            key = k.strip().lower()
            normalized[key] = val
        return normalized

class UserData(AppBaseModel):
    purchase_basics: PurchaseBasics
    family_travel: FamilyTravel
    needs_priorities: NeedsPriorities
    other_preferences: OtherPreferences