# Updated app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # You may need to pip install flask-cors
import requests
from bs4 import BeautifulSoup
import gemini
import logging # Import logging

app = Flask(__name__)
CORS(app) # Mitigates Cross-Origin Resource Sharing errorss
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Configure logging for app.py

@app.route('/parse-recipe', methods=['POST'])
def parse_recipe():
    # 1. Extract the URL sent by JavaScript
    data = request.get_json()
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

if __name__ == '__main__':
    # Starts the server on http://127.0.0.1:5000
    app.run(debug=True)