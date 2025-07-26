import os
import queue
import struct
import pvporcupine
import pyaudio
import wave
import whisper
import requests
import sounddevice as sd
import soundfile as sf
import asyncio
import edge_tts
from dotenv import load_dotenv
import re

# Load API key securely from .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not found in .env file.")

# Set up Porcupine hotword detection
PV_KEY = os.getenv("PV_ACCESS_KEY")
porcupine = pvporcupine.create(
    access_key=PV_KEY,
    keywords=["jarvis"]
)
pa = pyaudio.PyAudio()

audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎤 Listening for 'Jarvis'...")

# Load Whisper once
model = whisper.load_model("base")

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

#loading VAD
import webrtcvad
import collections
import time

def vad_record(pa, sample_rate=16000, aggressiveness=3, silence_limit=1.0, frame_duration=30):
    import collections
    import time

    vad = webrtcvad.Vad(aggressiveness)
    frame_length = int(sample_rate * frame_duration / 1000)  # samples per frame (e.g. 480)
    frame_size = frame_length * 2  # bytes per frame (16-bit samples)

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_length
    )

    print("🎙️ Start speaking (will stop after silence)...")

    frames = []
    silence_start = None
    ring_buffer = collections.deque(maxlen=int(silence_limit * 1000 / frame_duration))

    while True:
        frame = stream.read(frame_length, exception_on_overflow=False)
        if len(frame) != frame_size:
            # Incomplete frame, skip
            continue

        is_speech = vad.is_speech(frame, sample_rate)
        ring_buffer.append((frame, is_speech))

        if is_speech:
            silence_start = None
            frames.extend(f for f, speech in ring_buffer)
            ring_buffer.clear()
        else:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > silence_limit:
                break

    stream.stop_stream()
    stream.close()
    print("🛑 Silence detected, stopped recording.")
    return b"".join(frames)

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm_unpacked):
            print("🤖 Wake word detected!")

            # Record voice command
            command_filename = "user_command.wav"
            audio_bytes = vad_record(pa)
            with wave.open(command_filename, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)

            print("🧠 Transcribing...")
            result = model.transcribe(command_filename)
            user_text = result["text"]
            print(f"🗣️ You said: {user_text}")

            # Call the LLM (e.g., DeepSeek or Mistral via OpenRouter)
            print("🤖 Generating response...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "nousresearch/nous-hermes-2-mistral:free",
                    "messages": [
                        {"role": "system", "content": "You are JARVIS, an AI assistant modeled after the one in Iron Man. Maintain JARVIS sarcasm, wit and helpfulness. Keep your responses VERY short and concise. Your user is Nicole. Do not make any specific references to characters or plotlines from the Iron Man movie, for example do not mention Tony Stark, the suite or Pepper Potts. Avoid using stage directions or actions in asterisks like *beat*, *calibration pause*, or *adjusts tone*. Do not include theatrical or narrative indicators. Just speak directly to the user."},
                        {"role": "user", "content": user_text}
                    ]
                }
            )
            print("🧪 Raw response:", response.status_code, response.text)
            bot_text = response.json()["choices"][0]["message"]["content"]
            print(f"JARVIS: {bot_text}")

            # Speak it
            print("🎤 Speaking response...")
            asyncio.run(speak(bot_text))

except KeyboardInterrupt:
    print("\n🛑 Shutting down...")

finally:
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    porcupine.delete()