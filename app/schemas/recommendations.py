# app/schemas/meal.py

from pydantic import BaseModel, field_validator
from typing import Dict, Union


class Brand(BaseModel):
    name: str
    price: float
    sustainability_rating: str
    description: str

class RecommendedBrands(BaseModel):
    brands: list[Brand]
