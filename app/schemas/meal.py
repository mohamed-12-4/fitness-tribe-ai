# app/schemas/meal.py

from pydantic import BaseModel, field_validator
from typing import Dict, Union


class Meal(BaseModel):
    food_name: str
    total_calories: Union[int, float]
    calories_per_ingredient: Dict[str, Union[int, float]]
    total_protein: Union[int, float]
    total_carbohydrates: Union[int, float]
    total_fats: Union[int, float]
    
    @field_validator('total_calories', 'total_protein', 'total_carbohydrates', 'total_fats')
    @classmethod
    def convert_to_int(cls, v):
        """Convert float values to int by rounding"""
        if isinstance(v, float):
            return round(v)
        return v
    
    @field_validator('calories_per_ingredient')
    @classmethod
    def convert_ingredient_calories_to_int(cls, v):
        """Convert float calories in ingredients dict to int by rounding"""
        return {k: round(val) if isinstance(val, float) else val for k, val in v.items()}
