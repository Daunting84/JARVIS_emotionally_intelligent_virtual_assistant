import os
import re
import queue
import struct
import pyaudio
import wave
import whisper
import requests
import simpleaudio as sa
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf
import asyncio
import edge_tts
import torch
from recording import listen_for_command
from sending_neural_output import run_emotion_to_pose
from recording import listen_for_command, cleanup

print(torch.cuda.is_available())

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not found in .env file.")

# Edge TTS function
async def speak(text):
    text = clean_text(text)
    communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
    # Generate stream to memory
    tts_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            tts_bytes += chunk["data"]

    # Save to a temporary in-memory file and play
    with open("audio/temp_edge_tts.wav", "wb") as f:
        f.write(tts_bytes)
    data, fs = sf.read("audio/temp_edge_tts.wav", dtype='float32')
    sd.play(data, fs)
    sd.wait()

# Text cleanup
def clean_text(text):
    text = text.replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"[*]", "", text)
    return text

# Ensure audio directory exists
os.makedirs("audio", exist_ok=True)

try :
    while True:
        user_text = listen_for_command()

        run_emotion_to_pose(user_text)    

        print("🤖 Generating response...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [
                    {"role": "system", "content": "You are JARVIS, a refined AI assistant modeled after the one in Iron Man. Your user is Nicole, an engineering student. Do not make any specific references to characters or plotlines from the Iron Man movie, for example do not mention Pepper Potts. Keep your responses short. Avoid using stage directions or actions in asterisks like *beat*, *calibration pause*, or *adjusts tone*.Do not include theatrical or narrative indicators. Just speak directly and clearly to the user."},
                    {"role": "user", "content": user_text}
                ]
            }
        )
        print("🧪 Raw response:", response.status_code, response.text)
        bot_text = response.json()["choices"][0]["message"]["content"]
        print(f"🧾 JARVIS: {bot_text}")
        """
        def clean_text(text):
            text = text.replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'")
            text = re.sub(r"[*]", "", text)
            return text

        bot_text = clean_text(bot_text)
        sentences = bot_text.split(".")
        cleaned = [s.strip() for s in sentences if len(s.strip()) > 10]
        bot_text_cleaned = ". ".join(cleaned)
        """
          # Speak it
        print("🎤 Speaking response...")
        asyncio.run(speak(bot_text))

except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
finally:
    cleanup()