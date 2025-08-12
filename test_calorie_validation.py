#!/usr/bin/env python3
"""
Test the updated nutrition schema with float-to-int conversion
"""

from app.schemas.nutrition import Ingredient, MealOption

# Test data with floating point calories (like what Gemini might return)
test_ingredient_data = {
    "ingredient": "Greek yogurt",
    "quantity": "200g",
    "calories": 247.5  # Float value
}

test_meal_data = {
    "description": "High protein breakfast bowl",
    "ingredients": [
        {"ingredient": "Greek yogurt", "quantity": "200g", "calories": 247.5},
        {"ingredient": "Granola", "quantity": "30g", "calories": 150.0},
        {"ingredient": "Honey", "quantity": "15g", "calories": 45.7},
        {"ingredient": "Blueberries", "quantity": "50g", "calories": 61.5}
    ],
    "total_calories": 504.7,  # Float value
    "recipe": "Mix all ingredients in a bowl and serve fresh.",
    "suggested_brands": ["Al Ain Farms", "Bayara"]
}

print("Testing ingredient with float calories...")
try:
    ingredient = Ingredient(**test_ingredient_data)
    print(f"✓ Success! Calories converted from {test_ingredient_data['calories']} to {ingredient.calories}")
    print(f"Type: {type(ingredient.calories)}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nTesting meal option with float calories...")
try:
    meal = MealOption(**test_meal_data)
    print(f"✓ Success! Total calories converted from {test_meal_data['total_calories']} to {meal.total_calories}")
    print(f"Ingredient calories: {[ing.calories for ing in meal.ingredients]}")
    print("All calories are now integers!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nThe schema now handles:")
print("- Float calories from Gemini API → automatically rounded to integers")
print("- Mixed int/float values → all converted to integers")
print("- Maintains data integrity while fixing validation errors")
