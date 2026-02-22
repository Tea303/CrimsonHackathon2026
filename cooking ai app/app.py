#receives the data from js and processes it
import requests
from bs4 import BeautifulSoup # BeautifulSoup is not used in the current version of app.py, but kept for context.
import gemini # Import the gemini module

# 1. Define custom headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# NOTE: The original URL was a list of recipes. To extract a single recipe's details,
# you would typically navigate to an individual recipe page.
# For demonstration, we'll use a placeholder URL for a single recipe.
# You should replace this with an actual single recipe URL from allrecipes.com if you want to test the full extraction.
url = 'https://www.allrecipes.com/recipe/231988/twice-baked-potato-casserole-with-bacon/' # Example single recipe URL

# 2. Make the request, passing the headers to circumvent the security block
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Successfully bypassed the blocker!\n")
    
    # 3. Parse the raw HTML text using BeautifulSoup
    # The LLM will now "scan" the raw HTML content directly.
    html_content = response.text

    # The BeautifulSoup object 'soup' is no longer used for pre-extraction
    # as the LLM will now process the raw HTML.
    # If you need BeautifulSoup for other tasks, you can uncomment the line below,
    # but it won't be passed to the generate function for recipe extraction.
    # soup = BeautifulSoup(response.text, 'html.parser')

    print("--- Raw HTML Content for Gemini (Snippet) ---")
    # Printing a snippet to avoid overwhelming the console with very long HTML.
    # The full html_content is passed to the generate function.
    print(html_content[:500] + "...") 
    print("---------------------------------------------")

    # Call the Gemini AI to process the scraped text
    # Pass the raw HTML content directly to the generate function from the gemini module.
    json_output = gemini.generate(html_content)
    print("\n--- Gemini AI JSON Output ---")
    print(json_output)
    print("-----------------------------")
        
else:
    print(f"Error: Received status code {response.status_code}")