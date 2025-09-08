# app/schemas/workout.py

from pydantic import BaseModel
from typing import List, Optional
import sys
sys.path.append('/home/mohamed/Code/fitness-tribe-ai')
from app.schemas.nutrition import NutritionPlan

class ProfileData(BaseModel):
    weight: float  # in kilograms
    height: float  # in centimeters
    age: int
    sex: str
    goal: str  # bulking, shredding, fat loss, muscle building
    workouts_per_week: int
    equipment: List[str] = []  # List of available equipment (e.g., dumbbells, barbell, resistance bands)


class Exercise(BaseModel):
    exercise_id: str
    name: str
    sets: int
    reps: str  # could also be 'as many as possible'
    rest: int  # rest time in seconds


class WarmupCardioCooldown(BaseModel):
    description: str
    duration: int


class WorkoutSession(BaseModel):
    exercises: List[Exercise]


class WorkoutPlan(BaseModel):
    warmup: WarmupCardioCooldown
    cardio: WarmupCardioCooldown
    sessions_per_week: int
    workout_sessions: List[WorkoutSession]
    cooldown: WarmupCardioCooldown

class ExerciseResponse(BaseModel):
    text: str  # All text data not related to the generation
    data: Optional[WorkoutPlan]

class NutritionResponse(BaseModel):
    text: str  # All text data not related to the generation
    data: Optional[NutritionPlan]