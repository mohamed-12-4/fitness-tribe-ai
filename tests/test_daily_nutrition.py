#!/usr/bin/env python3
"""
Test script for the new daily nutrition plan functionality
"""

import json
from app.schemas.nutrition import ProfileData

# Example profile data with the new duration_days field
example_profile = {
    "weight": 70.0,
    "height": 175.0,
    "age": 25,
    "sex": "male",
    "goal": "muscle building",
    "dietary_preferences": ["high protein", "Mediterranean"],
    "food_intolerance": ["lactose"],
    "duration_days": 5  # Changed from duration_weeks to duration_days
}

# Create ProfileData instance
profile = ProfileData(**example_profile)

print("Example ProfileData for daily nutrition plan:")
print(json.dumps(profile.model_dump(), indent=2))

print("\nNew structure explanation:")
print("- duration_days: Number of days to generate meal plans for")
print("- Each day will have unique meals (breakfast, lunch, dinner, snacks)")
print("- Each day calculates its own total calories and macros")
print("- Dates are automatically assigned starting from today")
print("- No repeated meals across days for variety")

# Example API call structure
api_example = {
    "endpoint": "POST /nutrition-plans/generate",
    "request_body": example_profile,
    "expected_response_structure": {
        "daily_calories_range": {"min": 2200, "max": 2400},
        "macronutrients_range": {
            "protein": {"min": 140, "max": 160},
            "carbohydrates": {"min": 200, "max": 250},
            "fat": {"min": 70, "max": 90}
        },
        "daily_meal_plans": [
            {
                "day": 1,
                "date": "2025-08-12",
                "breakfast": {
                    "description": "...",
                    "ingredients": [{"ingredient": "...", "quantity": "...", "calories": 100}],
                    "total_calories": 450,
                    "recipe": "...",
                    "suggested_brands": ["Al Ain Farms", "Bayara"]
                },
                "lunch": {"description": "...", "total_calories": 600, "...": "..."},
                "dinner": {"description": "...", "total_calories": 700, "...": "..."},
                "snacks": [{"description": "...", "total_calories": 200, "...": "..."}],
                "total_daily_calories": 1950,
                "daily_macros": {"protein": 150, "carbohydrates": 220, "fat": 80}
            }
            # ... repeated for each day with different meals
        ],
        "total_days": 5
    }
}

print("\nAPI Usage Example:")
print(json.dumps(api_example, indent=2))
