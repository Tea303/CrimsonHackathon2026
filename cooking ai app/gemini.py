import os
import json
import logging # Import the logging module
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_json_text(text):
    """Cleans JSON text by removing Markdown code blocks."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate(content):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running the script.")

    client = genai.Client(
        api_key=api_key,
    )

    # Consider dropping to gemini-2.5-flash if 3-flash-preview still hits limits
    model = "gemini-2.5-flash-lite"
    
    # We enforce JSON output so it plugs perfectly into your frontend JavaScript
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1, # Low temperature for strict, predictable extraction
    )

    # F-string allows you to dynamically pass the scraped text from Flask
    prompt = f"""From the following text, extract the recipe title, ingredients, and steps.
    Format as JSON with keys: "title", "ingredients" (list of strings), "steps" (list of strings).
    Focus on the main recipe content and ignore any remaining irrelevant text.
    
    CONTENT:
    {content}
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=generate_content_config,
        )
        
        try:
            # Attempt to parse the response text as JSON
            cleaned_text = clean_json_text(response.text)
            json_output = json.loads(cleaned_text) # Ensure response.text is used
            logging.info(f"Gemini AI JSON Output:\n{json.dumps(json_output, indent=2)}") # Use logging
            return json_output # Return the parsed JSON object
        except json.JSONDecodeError as json_e:
            logging.error(f"JSON parsing error: {json_e}. Raw response text: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}") # Use logging for errors
        return None # Or raise the exception, depending on desired error handling

def answer_question_about_recipe(question: str, parsed_recipe_json: dict):
    """
    Answers a question about a recipe using the Gemini API.

    Args:
        question (str): The user's question about the recipe.
        parsed_recipe_json (dict): The previously parsed recipe in JSON format.

    Returns:
        dict: A JSON object containing the answer, or None if an error occurs.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set for ask_recipe_question.")
        return None

    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash-lite" # Switched to 2.5-flash-lite for consistency

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.5, # A slightly higher temperature for more conversational answers
    )

    # Convert the parsed recipe JSON back to a string for the prompt
    recipe_str = json.dumps(parsed_recipe_json, indent=2)

    prompt = f"""Based on the following recipe, answer the user's question.
    If the answer is not directly available in the recipe, state that.
    Format your response as JSON with a single key: "answer".

    RECIPE:
    {recipe_str}

    QUESTION: {question}
    """

    try:
        response = client.models.generate_content(model=model, contents=prompt, config=generate_content_config)
        cleaned_text = clean_json_text(response.text)
        return json.loads(cleaned_text)
    except Exception as e:
        logging.error(f"Error calling Gemini API for question answering: {e}")
        return None

if __name__ == "__main__":
    # Test it with a tiny payload first!
    print("--- Testing Recipe Parsing ---")
    recipe_data = generate("<html><body><h1>Test Recipe</h1><ul><li>Ingredient 1</li></ul><ol><li>Step 1</li></ol></body></html>")
    
    if recipe_data:
        print("\n--- Testing Question Answering ---")
        answer = answer_question_about_recipe("What is the first step?", recipe_data)
        print(json.dumps(answer, indent=2))
