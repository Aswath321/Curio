import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Get EDAMAM API KEY
APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

prompt_template5 = """
You are an assistant that helps in identifying recipes.
For the query: {query}
Please identify the recipe or food item the user is asking about and return it in this exact JSON format:
{{
    "name": "tool_name",
    "parameters": {{
        "text": "your detailed recipe response here"
    }}
}}
"""

def format_recipe_output(recipes_list):
    """Format the recipes into a clean text output"""
    if not recipes_list:
        return "No recipes found for your query."
    
    formatted_output = "Here are some recipes I found:\n\n"
    for recipe in recipes_list:
        formatted_output += f"🍳 {recipe['label']}\n"
        formatted_output += f"📝 Ingredients:\n{', '.join(recipe['ingredients'])}\n"
        formatted_output += f"🔥 Calories: {recipe['calories']:.0f}\n"
        formatted_output += f"🔗 Recipe URL: {recipe['url']}\n"
        formatted_output += f"👩‍🍳 Source: {recipe['source']}\n"
        formatted_output += "=" * 50 + "\n\n"
    
    return formatted_output

def get_recipes(query):
    try:
        # First, get the cleaned food item query
        response = model.generate_content(prompt_template5.format(query=query))
        
        # Make the API request to Edamam
        url = 'https://api.edamam.com/search'
        params = {
            'q': query,
            'app_id': APP_ID,
            'app_key': APP_KEY,
            'from': 0,
            'to': 5
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            recipes = []
            
            if data['hits']:
                for recipe in data['hits']:
                    recipe_info = recipe['recipe']
                    recipes.append({
                        'label': recipe_info['label'],
                        'url': recipe_info['url'],
                        'ingredients': recipe_info['ingredientLines'],
                        'calories': recipe_info['calories'],
                        'source': recipe_info['source']
                    })
                
                formatted_output = format_recipe_output(recipes)
            else:
                formatted_output = "No recipes found for your query."
        else:
            formatted_output = f"Error: Unable to fetch recipes. Status code: {response.status_code}"
        
        # Return in the format expected by AgentRes
        return {
            "name": "recipe",
            "parameters": {
                "text": formatted_output
            }
        }
        
    except Exception as e:
        # Return error in the format expected by AgentRes
        return {
            "name": "final_answer",
            "parameters": {
                "text": f"I apologize, but I encountered an error while fetching recipes: {str(e)}"
            }
        }