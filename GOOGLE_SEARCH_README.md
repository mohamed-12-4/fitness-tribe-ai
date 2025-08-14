# Google Search Integration with Gemini

This implementation adds Google search capabilities to your Gemini model, replacing the Open Food Facts API with a more versatile search tool.

## 🔧 Setup

### 1. Get SERP API Key

1. Visit [SerpApi](https://serpapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file:
   ```
   SERP_API_KEY=your_actual_serp_api_key_here
   ```

### 2. Configuration

The Google search tool is automatically configured as a function tool for the Gemini model in `gemini_model.py`.

## 🛠️ How It Works

### Tool Definition

The Google search is defined as a function tool that the Gemini model can call:

```python
google_search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="google_search",
            description="Search Google for information about food, nutrition, recipes, or any general topic",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="The search query to look up information"
                    ),
                    "num_results": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of search results to return (default: 5)"
                    )
                },
                required=["query"]
            )
        )
    ]
)
```

### Function Implementation

The search function uses SERP API to get Google search results:

```python
def google_search(query: str, num_results: int = 5) -> Optional[Dict]:
    """Search Google using SERP API for general information"""
    # Returns structured data with:
    # - organic_results: List of search results
    # - knowledge_graph: Knowledge panel data if available
    # - query: Original search query
    # - total_results: Number of results returned
```

### Integration in Methods

All three main methods now support Google search:

1. **`analyze_meal()`**: Can search for nutritional information about specific foods
2. **`generate_workout_plan()`**: Can research exercise techniques and safety information
3. **`generate_nutrition_plan()`**: Can look up current dietary guidelines and food information

## 🚀 Usage Examples

### Direct Search

```python
from app.models.gemini_model import GeminiModel

# Direct search
result = GeminiModel.google_search("chicken breast nutrition facts", 5)
print(result)
```

### Model with Grounding

When you use the model methods, it will automatically use Google search when needed:

```python
# The model will automatically search for information when analyzing meals
result = GeminiModel.analyze_meal(image_data)

# The model can search for exercise information when creating workout plans
workout = GeminiModel.generate_workout_plan(profile_data)

# The model can search for nutritional information when creating meal plans
nutrition_plan = GeminiModel.generate_nutrition_plan(profile_data)
```

## 🧪 Testing

Run the test scripts to verify everything works:

```bash
# Test the search functionality
python test_google_search.py

# See a full example with Gemini integration
python example_google_search.py
```

## ✨ Benefits

1. **Real-time Information**: Get current, up-to-date information instead of static API data
2. **Broader Coverage**: Search for any topic, not just food items
3. **Grounded Responses**: Model responses are based on actual search results
4. **Versatility**: Can research exercises, nutrition, recipes, ingredients, and more
5. **Knowledge Graph**: Access to Google's knowledge panels for rich, structured data

## 🔄 Migration from Open Food Facts

The previous `search_food_info()` method has been replaced with `google_search()`. Key differences:

- **Broader scope**: Not limited to food products
- **Current data**: Real-time search results instead of database entries
- **Rich context**: Full search snippets instead of just nutritional values
- **Flexibility**: Can search for recipes, cooking tips, exercise information, etc.

## 📊 Response Format

Search results are returned in this format:

```json
{
  "query": "chicken breast nutrition",
  "organic_results": [
    {
      "title": "Chicken Breast Nutrition Facts",
      "link": "https://example.com",
      "snippet": "Chicken breast contains...",
      "position": 1
    }
  ],
  "knowledge_graph": {
    "title": "Chicken breast",
    "description": "Chicken breast is...",
    "source": "Wikipedia"
  },
  "total_results": 5
}
```

This provides much richer context for the AI model to generate accurate, well-informed responses.
