import requests
from playsound import playsound
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# 1. Added 'content' as a parameter to the function
def test_elevenlabs(content):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    
    # 2. Replaced the hardcoded string with the 'content' variable
    data = {"text": content, "model_id": "eleven_multilingual_v2"}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        playsound("output.mp3")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    ai_response = "First, dice the onions and sauté them until translucent."
    test_elevenlabs(ai_response)