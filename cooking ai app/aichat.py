import requests
import base64
import os
import time

# Configuration
ELEVENLABS_API_KEY = "sk_09bc2162234b0d86624fe4688fc7edd77efd45385b16eb1f"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

def generate_audio_base64(text):
    """
    Generates audio from text using ElevenLabs and returns it as a base64 string.
    This is useful for sending audio to the frontend.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"ElevenLabs API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception generating audio: {e}")
    return None

if __name__ == "__main__":
    print("Testing Audio Generation...")
    # Test generating audio (without playing it, to avoid blocking/freezing)
    b64_audio = generate_audio_base64("This is a test of the cooking assistant voice.")
    if b64_audio:
        print(f"Success! Generated {len(b64_audio)} bytes of base64 audio data.")
    else:
        print("Failed to generate audio.")