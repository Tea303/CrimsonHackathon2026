import requests
from playsound import playsound #pip install playsound==1.2.2

ELEVENLABS_API_KEY = "sk_09bc2162234b0d86624fe4688fc7edd77efd45385b16eb1f"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

def test_elevenlabs():
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": "Hello, this is a test of the Eleven Labs text-to-speech API.",
        "model_id": "eleven_multilingual_v2"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)

        print("✅ SUCCESS — output.mp3 created")
        print("🔊 Playing audio...")

        playsound("output.mp3")
    else:
        print("❌ ERROR:", response.status_code)
        print(response.text)


if __name__ == "__main__":
    test_elevenlabs()