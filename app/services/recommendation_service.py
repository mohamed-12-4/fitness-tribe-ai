# app/services/recommendation_service.py

from app.models.gemini_model import GeminiModel
from app.schemas.recommendations import RecommendedBrands, Brand
from fastapi import HTTPException
import json
import logging


def clean_response_text(response_text: str) -> str:
    """Strip unnecessary markdown or whitespace that might have been included"""
    clean_text = response_text.strip("```json").strip("```").strip()
    return clean_text


def get_brand_recommendations(product: str) -> RecommendedBrands:
    """
    Get brand recommendations for a given product using AI.
    
    Args:
        product (str): The product name to get brand recommendations for
        
    Returns:
        RecommendedBrands: Pydantic model containing list of recommended brands
        
    Raises:
        HTTPException: If there's an error in processing or validation
    """
    try:
        # Call the Gemini model to get brand recommendations
        result_text = GeminiModel.recommend_brands(product)
        
        if not result_text:
            raise HTTPException(status_code=500, detail="No response from Gemini API")
        
        # Clean the result text to remove any markdown formatting
        clean_result_text = clean_response_text(result_text)
        
        # Parse the JSON response
        try:
            result = json.loads(clean_result_text)
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error (Brand Recommendations): {str(e)}")
            logging.error(f"Cleaned Result Text: {clean_result_text}")
            raise HTTPException(status_code=500, detail=f"JSON Decode Error: {str(e)}")
        
        # Convert the result to Pydantic models
        brands = []
        for brand_data in result.get("brands", []):
            try:
                brand = Brand(**brand_data)
                brands.append(brand)
            except Exception as e:
                logging.warning(f"Skipping invalid brand data: {brand_data}, error: {str(e)}")
                continue
        
        if not brands:
            raise HTTPException(status_code=404, detail="No valid brand recommendations found")
        
        return RecommendedBrands(brands=brands)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Exception (Brand Recommendations): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
