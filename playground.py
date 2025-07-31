import requests

def find_healthy_products(category):
    """
    args:
    category (str): The category of products to search for.
    Returns a list of healthy products in the specified category.
    """
    headers = {
        "User-Agent": "Sustainahealth/1.0 (mohamed_2005_12@outlook.com)"
    }
    params = {
      "categories_tags_en": category,
      "nutrition_grades_tags": "a|b",
      ##"ecoscore_tags": "a|b",
      "cc": "ae",
      "fields": "code,product_name,brands,nutrition_grades,ecoscore_grade,image_url",
      "page_size": 20
    }
    resp = requests.get("https://world.openfoodfacts.org/api/v2/search", headers=headers, params=params)

    if resp.status_code != 200:
        raise Exception(f"Error fetching data: {resp.status_code}")
    print(resp.text)
    data = resp.json()
    print(data)
    return data.get("products", [])

# Use it like:
cereals = find_healthy_products("eggs")
print(cereals)