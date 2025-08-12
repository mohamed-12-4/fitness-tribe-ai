from app.models.gemini_model import GeminiModel
from app.schemas.nutrition import (
    ProfileData,
    NutritionPlan,
    MealOption,
    DailyMealPlan,
    DailyCaloriesRange,
    MacronutrientRange,
)
from fastapi import HTTPException
import json
import logging
from datetime import datetime, timedelta


def clean_response_text(response_text: str) -> str:
    # Strip unnecessary markdown or whitespace that might have been included
    clean_text = response_text.strip("```json").strip("```").strip()
    return clean_text


def generate_nutrition_plan(profile_data: ProfileData) -> NutritionPlan:
    try:
        result_text = GeminiModel.generate_nutrition_plan(profile_data.model_dump())

        if not result_text:
            raise HTTPException(status_code=500, detail="No response from Gemini API")

        # Clean the result_text to remove Markdown formatting
        clean_result_text = clean_response_text(result_text)

        # Directly parse the cleaned result text
        try:
            result = json.loads(clean_result_text)
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error (Provide Nutrition Advice): {str(e)}")
            logging.error(
                f"Cleaned Result Text (Provide Nutrition Advice) on JSON Decode Error: {clean_result_text}"
            )
            raise HTTPException(status_code=500, detail=f"JSON Decode Error: {str(e)}")

        # Convert the result dictionary to Pydantic models
        daily_calories_range = DailyCaloriesRange(**result["daily_calories_range"])
        macronutrients_range = {
            k: MacronutrientRange(**v)
            for k, v in result["macronutrients_range"].items()
        }

        def parse_meal_option(meal_data):
            return MealOption(**meal_data)

        # Parse daily meal plans
        daily_meal_plans = []
        start_date = datetime.now().date()
        
        for i, daily_plan_data in enumerate(result.get("daily_meal_plans", [])):
            # Add actual dates to the daily plans
            plan_date = start_date + timedelta(days=i)
            daily_plan_data['date'] = plan_date.strftime('%Y-%m-%d')
            daily_plan_data['day'] = i + 1
            
            # Parse meal options for this day
            breakfast = parse_meal_option(daily_plan_data["breakfast"])
            lunch = parse_meal_option(daily_plan_data["lunch"])
            dinner = parse_meal_option(daily_plan_data["dinner"])
            snacks = [parse_meal_option(snack) for snack in daily_plan_data["snacks"]]
            
            daily_meal_plan = DailyMealPlan(
                day=daily_plan_data["day"],
                date=daily_plan_data["date"],
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                snacks=snacks,
                total_daily_calories=daily_plan_data.get("total_daily_calories", 0),
                daily_macros=daily_plan_data.get("daily_macros", {})
            )
            daily_meal_plans.append(daily_meal_plan)

        return NutritionPlan(
            daily_calories_range=daily_calories_range,
            macronutrients_range=macronutrients_range,
            daily_meal_plans=daily_meal_plans,
            total_days=result.get("total_days", len(daily_meal_plans))
        )

    except Exception as e:
        logging.error(f"Exception (Provide Nutrition Advice): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
