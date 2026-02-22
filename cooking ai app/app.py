from flask import Flask, request, jsonify
from flask_cors import CORS # You may need to pip install flask-cors
import requests # Keep requests for web scraping
from bs4 import BeautifulSoup
import gemini # Import the entire gemini module
import logging # Import logging
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) # Mitigates Cross-Origin Resource Sharing errorss
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Configure logging for app.py

@app.route('/parse-recipe', methods=['POST'])
def parse_recipe():
    # 1. Extract the URL sent by JavaScript
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    target_url = data.get('url')

    if not target_url:
        logging.warning("No URL provided in the request.")
        return jsonify({"error": "No URL provided"}), 400 #

    # 2. Scrape the content
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(target_url, headers=headers, timeout=10) # Add a timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch website {target_url}: {e}")
        return jsonify({"error": f"Failed to fetch website: {e}"}), 500 #

    # 3. Clean the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            json_ld_data = json.loads(script.string)
            # JSON-LD can be a list or a dict. Search for the "Recipe" schema.
            if isinstance(json_ld_data, list):
                for item in json_ld_data:
                    if item.get('@type') == 'Recipe':
                        return jsonify({
                            "title": item.get('name'),
                            "ingredients": item.get('recipeIngredient'),
                            "steps": [step.get('text') for step in item.get('recipeInstructions', [])]
                        }), 200
            elif json_ld_data.get('@type') == 'Recipe':
                 return jsonify({
                     "title": json_ld_data.get('name'),
                     "ingredients": json_ld_data.get('recipeIngredient'),
                     "steps": [step.get('text') for step in json_ld_data.get('recipeInstructions', [])]
                 }), 200
        except Exception:
            continue # If JSON-LD fails, fallback to Gemini

    for element in soup(["script", "style", "header", "footer", "nav", "aside", "meta", "iframe"]):
        element.decompose()
    
    cleaned_content = soup.get_text(separator='\n', strip=True)
    logging.debug(f"Cleaned content length: {len(cleaned_content)}") # Log content length for debugging

    # 4. Pass the cleaned content to the Gemini module
    try:
        json_output = gemini.generate(cleaned_content)
        
        if json_output:
            # Send the AI-generated JSON back to JavaScript
            return jsonify(json_output), 200 #
        else:
            # gemini.generate already logs the specific error
            return jsonify({"error": "AI failed to parse recipe. Check server logs for details."}), 500 #

    except Exception as e:
        logging.exception("An unexpected error occurred during Gemini processing.") # Logs traceback
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500 #

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def generate_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Return base64 encoded audio
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        logging.error(f"ElevenLabs API Error: {e}")
    return None

@app.route('/ask-recipe', methods=['POST'])
def ask_recipe():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    question = data.get('question')
    # It's crucial that the frontend sends the previously parsed recipe JSON
    # so the LLM has context for the question.
    parsed_recipe = data.get('recipe_context') 

    if not question or not parsed_recipe:
        logging.warning("Missing 'question' or 'recipe_context' in /ask-recipe request.")
        return jsonify({"error": "Missing 'question' or 'recipe_context'"}), 400

    try:
        # Call the new Gemini function to answer the question about the recipe
        ai_answer = gemini.answer_question_about_recipe(question, parsed_recipe)

        if ai_answer:
            # Generate audio for the answer
            answer_text = ai_answer.get('answer')
            if answer_text:
                audio_b64 = generate_audio(answer_text)
                if audio_b64:
                    ai_answer['audio_base64'] = audio_b64
            return jsonify(ai_answer), 200
        else:
            return jsonify({"error": "AI failed to answer the question. Check server logs for details."}), 500
    except Exception as e:
        logging.exception("An unexpected error occurred during Gemini question answering.")
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Keep debug=True for error logs, but turn off the reloader
    app.run(debug=True, use_reloader=False)