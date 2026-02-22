import os
from google import genai
from google.genai import types

def generate(scraped_recipe_text):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Consider dropping to gemini-2.5-flash if 3-flash-preview still hits limits
    model = "gemini-3-flash-preview" 
    
    # We enforce JSON output so it plugs perfectly into your frontend JavaScript
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1, # Low temperature for strict, predictable extraction
    )

    # F-string allows you to dynamically pass the scraped text from Flask
    prompt = f"""
    Extract the recipe title, ingredients, and steps from the following text. 
    Format as JSON with keys: "title", "ingredients" (list of strings), "steps" (list of strings).
    
    TEXT:
    {scraped_recipe_text}
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=generate_content_config,
    )
    
    print(response.text)
    return response.text

if __name__ == "__main__":
    # Test it with a tiny payload first!
    generate("How to make toast: 1. Get bread. 2. Put in toaster.")