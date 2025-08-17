#!/usr/bin/env python3
"""
Test script for brand recommendation functionality
"""

import requests
import json

# Test the brand recommendation endpoint
def test_brand_recommendations():
    base_url = "http://localhost:8000"
    
    # Test products
    test_products = [
        "organic olive oil",
        "quinoa",
        "almond milk",
        "greek yogurt",
        "protein powder",
        "green tea"
    ]
    
    print("Testing Brand Recommendation API")
    print("=" * 50)
    
    for product in test_products:
        print(f"\n🔍 Getting recommendations for: {product}")
        
        try:
            response = requests.get(
                f"{base_url}/recommendations/brands",
                params={"product": product},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data['brands'])} recommendations:")
                
                for i, brand in enumerate(data['brands'], 1):
                    print(f"  {i}. {brand['name']}")
                    print(f"     💰 Price: {brand['price']} AED")
                    print(f"     🌱 Sustainability: {brand['sustainability_rating']}")
                    print(f"     📝 {brand['description'][:80]}...")
                    print()
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

# Example API usage
def show_api_usage():
    print("\n" + "=" * 50)
    print("API Usage Examples:")
    print("=" * 50)
    
    examples = {
        "Basic request": "GET /recommendations/brands?product=organic olive oil",
        "Curl command": "curl 'http://localhost:8000/recommendations/brands?product=quinoa'",
        "Python requests": """
import requests
response = requests.get(
    'http://localhost:8000/recommendations/brands',
    params={'product': 'greek yogurt'}
)
print(response.json())
        """,
        "Expected response format": {
            "brands": [
                {
                    "name": "Al Ain Farms",
                    "price": 25.0,
                    "sustainability_rating": "Excellent",
                    "description": "Local UAE brand known for organic and sustainable practices..."
                },
                {
                    "name": "Bayara",
                    "price": 30.0,
                    "sustainability_rating": "Good",
                    "description": "Premium quality nuts and dried fruits with eco-friendly packaging..."
                }
            ]
        }
    }
    
    for title, content in examples.items():
        print(f"\n{title}:")
        if isinstance(content, dict):
            print(json.dumps(content, indent=2))
        else:
            print(content)

if __name__ == "__main__":
    print("Brand Recommendation API Test")
    print("Make sure your FastAPI server is running on localhost:8000")
    print("Start it with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    
    choice = input("\nDo you want to test the API now? (y/n): ").lower()
    if choice == 'y':
        test_brand_recommendations()
    
    show_api_usage()
