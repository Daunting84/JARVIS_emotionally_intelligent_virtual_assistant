import os
import requests
from dotenv import load_dotenv
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.models.xtts import XttsArgs
from recording import listen_for_command

torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs,
])

def get_emotion_and_avd(user_text):
    load_dotenv()
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not found in .env file.")

    print("🤖 Generating emotion output...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek/deepseek-chat-v3-0324",
            "messages": [
                {"role": "system", "content": "You are the emotional engine of JARVIS, an AI assistant based off of Iron Man. The user will converse with you, and your job is to output the emotion that the listener would feel in response to the users dialog. Output only one word for the emotion name. you must also output the emotions associated Arrousal, Valence, Dominance values. AVD values must be between between -1.7 and 1.7. Your ouput must follow the following format : ('emotion_name',[A,V,D])"},
                {"role": "user", "content": user_text}
            ]
        }
    )
    print("🧪 Raw response:", response.status_code, response.text)
    bot_text = response.json()["choices"][0]["message"]["content"]
    print(f"🧾 Emotion Output: {bot_text}")

    return bot_text