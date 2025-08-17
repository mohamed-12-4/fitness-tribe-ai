# app/routers/recommendations.py

from fastapi import APIRouter, HTTPException, Query
from app.schemas.recommendations import RecommendedBrands
from app.services.recommendation_service import get_brand_recommendations

router = APIRouter()


@router.get("/brands", response_model=RecommendedBrands)
async def recommend_brands(
    product: str = Query(..., description="Product name to get brand recommendations for", min_length=2, max_length=100)
):
    """
    Get brand recommendations for a specific product.
    
    This endpoint provides UAE-based and sustainable brand recommendations
    for any given product, including pricing information, sustainability
    ratings, and detailed descriptions.
    
    Args:
        product: The name of the product to get recommendations for
        
    Returns:
        RecommendedBrands: List of recommended brands with details
        
    Example:
        GET /recommendations/brands?product=organic olive oil
    """
    try:
        return get_brand_recommendations(product)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
