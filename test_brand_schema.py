#!/usr/bin/env python3
"""
Test the brand recommendation schema validation
"""

from app.schemas.recommendations import Brand, RecommendedBrands
import json

def test_brand_schema():
    """Test the Brand and RecommendedBrands schemas"""
    
    print("Testing Brand Recommendation Schemas")
    print("=" * 40)
    
    # Test single brand creation
    print("\n1. Testing Brand schema:")
    try:
        brand_data = {
            "name": "Al Ain Farms",
            "price": 25.50,
            "sustainability_rating": "Excellent",
            "description": "Local UAE brand known for fresh dairy products and sustainable farming practices."
        }
        
        brand = Brand(**brand_data)
        print(f"✅ Brand created successfully:")
        print(f"   Name: {brand.name}")
        print(f"   Price: {brand.price} AED")
        print(f"   Rating: {brand.sustainability_rating}")
        print(f"   Description: {brand.description[:50]}...")
        
    except Exception as e:
        print(f"❌ Error creating brand: {e}")
    
    # Test RecommendedBrands with multiple brands
    print("\n2. Testing RecommendedBrands schema:")
    try:
        brands_data = {
            "brands": [
                {
                    "name": "Al Ain Farms",
                    "price": 25.50,
                    "sustainability_rating": "Excellent",
                    "description": "Local UAE brand known for fresh dairy products and sustainable farming."
                },
                {
                    "name": "Bayara",
                    "price": 30.00,
                    "sustainability_rating": "Good",
                    "description": "Premium nuts and dried fruits with eco-friendly packaging."
                },
                {
                    "name": "Kibsons",
                    "price": 35.75,
                    "sustainability_rating": "Excellent",
                    "description": "Fresh organic produce delivery service in UAE with zero-waste packaging."
                }
            ]
        }
        
        recommended_brands = RecommendedBrands(**brands_data)
        print(f"✅ RecommendedBrands created successfully with {len(recommended_brands.brands)} brands:")
        
        for i, brand in enumerate(recommended_brands.brands, 1):
            print(f"   {i}. {brand.name} - {brand.price} AED ({brand.sustainability_rating})")
            
    except Exception as e:
        print(f"❌ Error creating RecommendedBrands: {e}")
    
    # Test JSON serialization
    print("\n3. Testing JSON serialization:")
    try:
        json_output = recommended_brands.model_dump()
        json_str = json.dumps(json_output, indent=2)
        print("✅ JSON serialization successful:")
        print(json_str[:200] + "..." if len(json_str) > 200 else json_str)
        
    except Exception as e:
        print(f"❌ Error with JSON serialization: {e}")

if __name__ == "__main__":
    test_brand_schema()
