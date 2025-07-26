import os
import struct
import pvporcupine
import pyaudio
import wave
import whisper
from dotenv import load_dotenv
import ast

load_dotenv()

PV_KEY = os.getenv("PV_ACCESS_KEY")

# Initialize Porcupine and PyAudio ONCE globally
porcupine = pvporcupine.create(access_key=PV_KEY, keywords=["jarvis"])
pa = pyaudio.PyAudio()

# Open the stream once here
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

model = whisper.load_model("base")

def listen_for_command():
    print("🎤 Listening for 'Jarvis'...")

    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm_unpacked):
            print("🤖 Wake word detected!")

            # Record voice command
            record_seconds = 5
            command_filename = "user_command.wav"
            print(f"🎙️ Recording for {record_seconds} seconds...")

            frames = []
            record_stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )

            for _ in range(0, int(16000 / 1024 * record_seconds)):
                data = record_stream.read(1024, exception_on_overflow=False)
                frames.append(data)

            record_stream.stop_stream()
            record_stream.close()

            wf = wave.open(command_filename, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b"".join(frames))
            wf.close()

            print("🧠 Transcribing...")
            result = model.transcribe(command_filename)
            user_text = result["text"]
            print(f"🗣️ You said: {user_text}")

            return user_text

def cleanup():
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    pa.terminate()