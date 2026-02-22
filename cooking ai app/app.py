#receives the data from js and processes it
import requests
from bs4 import BeautifulSoup
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
    
    # 3. Parse and Clean the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove script, style, and other irrelevant tags to reduce token count
    for element in soup(["script", "style", "header", "footer", "nav", "aside", "meta", "iframe"]):
        element.decompose()

    # Extract text with separators to maintain some structure
    cleaned_content = soup.get_text(separator='\n', strip=True)

    print("--- Cleaned Text Content for Gemini (Snippet) ---")
    print(cleaned_content[:5000] + "...") 
    print("-------------------------------------------------")

    # Call the Gemini AI to process the scraped text
    json_output = gemini.generate(cleaned_content)
    print("\n--- Gemini AI JSON Output ---")
    print(json_output)
    print("-----------------------------")
        
else:
    print(f"Error: Received status code {response.status_code}")