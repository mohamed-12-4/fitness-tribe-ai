from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Union


# Define ProfileData model
class ProfileData(BaseModel):
    weight: float  # in kilograms
    height: float  # in centimeters
    age: int
    sex: str  # "male" or "female"
    goal: str  # bulking, shredding, fat loss, muscle building
    dietary_preferences: Optional[List[str]] = (
        None  # e.g., ["vegetarian", "high protein, pescatarian, vegan"]
    )
    food_intolerance: Optional[List[str]] = None  # e.g. ["dairy", "gluten", "caffeine"]
    duration_days: int  # Changed from duration_weeks to duration_days


class MacronutrientRange(BaseModel):
    min: int
    max: int


class DailyCaloriesRange(BaseModel):
    min: int
    max: int


class Ingredient(BaseModel):
    ingredient: str
    quantity: str
    calories: Union[int, float]
    
    @field_validator('calories')
    @classmethod
    def convert_calories_to_int(cls, v):
        """Convert float calories to int by rounding"""
        if isinstance(v, float):
            return round(v)
        return v


class MealOption(BaseModel):
    description: str
    ingredients: List[Ingredient]
    total_calories: Union[int, float]
    recipe: str
    suggested_brands: List[str]
    
    @field_validator('total_calories')
    @classmethod
    def convert_total_calories_to_int(cls, v):
        """Convert float total_calories to int by rounding"""
        if isinstance(v, float):
            return round(v)
        return v


class DailyMealPlan(BaseModel):
    day: int  # Day number (1, 2, 3, etc.)
    date: str  # Date in YYYY-MM-DD format
    breakfast: MealOption
    lunch: MealOption
    dinner: MealOption
    snacks: List[MealOption]  # Can have multiple snacks per day
    total_daily_calories: Union[int, float]
    daily_macros: Dict[str, float]  # protein, carbs, fat in grams
    
    @field_validator('total_daily_calories')
    @classmethod
    def convert_daily_calories_to_int(cls, v):
        """Convert float total_daily_calories to int by rounding"""
        if isinstance(v, float):
            return round(v)
        return v


class NutritionPlan(BaseModel):
    daily_calories_range: DailyCaloriesRange
    macronutrients_range: Dict[str, MacronutrientRange]
    daily_meal_plans: List[DailyMealPlan]  # List of daily plans
    total_days: int
