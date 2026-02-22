import requests
from playsound import playsound
import time

ELEVENLABS_API_KEY = "sk_09bc2162234b0d86624fe4688fc7edd77efd45385b16eb1f"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

def speak(content):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    
    response = requests.post(url, json={"text": content, "model_id": "eleven_multilingual_v2"}, headers=headers)

    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        time.sleep(0.2) 
        playsound("output.mp3")