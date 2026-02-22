import os
from google import genai
from google.genai import types
import json # Import the json module for parsing

def generate(html_content):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running the script.")

    client = genai.Client(
        api_key=api_key,
    )

    # Consider dropping to gemini-2.5-flash if 3-flash-preview still hits limits
    model = "gemini-3-flash-preview" 
    
    # We enforce JSON output so it plugs perfectly into your frontend JavaScript
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1, # Low temperature for strict, predictable extraction
    )

    # F-string allows you to dynamically pass the scraped text from Flask
    prompt = f"""From the following HTML content, extract the recipe title, ingredients, and steps.
    Format as JSON with keys: "title", "ingredients" (list of strings), "steps" (list of strings).
    Focus on the main recipe content and ignore navigation, ads, or other irrelevant HTML elements.
    
    HTML CONTENT:
    {html_content}
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=generate_content_config,
        )
        
        # Attempt to parse the response text as JSON
        json_output = json.loads(response.text)
        print(json.dumps(json_output, indent=2)) # Pretty print the JSON
        return json_output # Return the parsed JSON object
    except Exception as e:
        print(f"Error calling Gemini API or parsing response: {e}")
        return None # Or raise the exception, depending on desired error handling

if __name__ == "__main__":
    # Test it with a tiny payload first!
    generate("<html><body><h1>Test Recipe</h1><ul><li>Ingredient 1</li></ul><ol><li>Step 1</li></ol></body></html>")
