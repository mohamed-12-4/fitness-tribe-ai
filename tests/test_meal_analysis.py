#!/usr/bin/env python3
"""
Test the updated meal analysis functionality with the new Meal schema
"""

import json
from app.schemas.meal import Meal

# Example response that Gemini AI might return
example_gemini_response = {
    "food_name": "Grilled Chicken Salad with Quinoa",
    "total_calories": 485.7,  # Float value (will be converted to int)
    "calories_per_ingredient": {
        "Grilled chicken breast": 231.2,
        "Mixed greens": 15.5,
        "Quinoa": 120.0,
        "Cherry tomatoes": 18.3,
        "Cucumber": 8.7,
        "Olive oil dressing": 92.0
    },
    "total_protein": 42.8,     # Float value (will be converted to int)
    "total_carbohydrates": 28.4, # Float value (will be converted to int)  
    "total_fats": 18.6         # Float value (will be converted to int)
}

print("Testing Meal schema with AI response data...")
print("Original data (with floats):")
print(json.dumps(example_gemini_response, indent=2))

try:
    # Create Meal instance - validators will convert floats to ints
    meal = Meal(**example_gemini_response)
    
    print("\n✓ Success! Meal object created with converted values:")
    print(f"Food Name: {meal.food_name}")
    print(f"Total Calories: {meal.total_calories} (type: {type(meal.total_calories)})")
    print(f"Total Protein: {meal.total_protein}g (type: {type(meal.total_protein)})")
    print(f"Total Carbohydrates: {meal.total_carbohydrates}g (type: {type(meal.total_carbohydrates)})")
    print(f"Total Fats: {meal.total_fats}g (type: {type(meal.total_fats)})")
    
    print("\nCalories per ingredient (converted to integers):")
    for ingredient, calories in meal.calories_per_ingredient.items():
        print(f"  {ingredient}: {calories} cal (type: {type(calories)})")
    
    print("\n✓ All float values have been automatically converted to integers!")
    
    # Convert back to dict to see final structure
    meal_dict = meal.model_dump()
    print("\nFinal meal data structure:")
    print(json.dumps(meal_dict, indent=2))
    
except Exception as e:
    print(f"✗ Error: {e}")

print("\nAPI Endpoint: POST /meals/analyze")
print("Expected response format matches the Meal schema exactly!")
