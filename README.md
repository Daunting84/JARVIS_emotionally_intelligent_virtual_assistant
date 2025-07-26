# 🤖 Jarvis: Emotionally Intelligent AI Assistant

### 📘 Project Overview

Inspired by Iron Man's virtual assistant, **Jarvis** is a Unity-based, AI-powered character that listens to your voice, generates natural language responses using an LLM, detects the emotional tone behind your conversation, and *physically reacts* using facial expressions and body language via a custom-trained neural network.

By combining speech recognition, emotional modeling, neural net prediction, and 3D animation, Jarvis brings emotional intelligence to virtual assistants—and lays the foundation for real-world robotics.

---

### 💡 My Inspiration

All summer, I've been dreaming of building a network of neural networks that simulate a human-like brain and connect it to a robotic body. This version of Jarvis is the first step, combining emotion recognition, speech, and animation. Inspired by characters like Baymax and Iron Man's AI, I spent months learning how to build neural networks, rig 3D models, and integrate LLMs.

Jarvis is the result of that work—and it's just the beginning.

---

### 🔧 Architecture

Jarvis is made of several modular components working together:

- **Wake Word Activation** using [Porcupine](https://github.com/Picovoice/porcupine)
- **Speech-to-Text** using [OpenAI Whisper]
- **LLM Processing** using [OpenRouter API + DeepSeek]
  - First module: Generates a **spoken response**
  - Second module: Determines the **emotional tone** via Arousal, Valence, Dominance (AVD)
- **TTS** using Microsoft Edge's neural voice engine
- **Emotion-to-Pose Neural Net**:
  - Transforms AVD values into bone angles for animation
- **Unity Character Animation**:
  - Receives joint angles via a Flask API
  - Moves the rigged character using custom C# code

---

### 🧠 What Makes This Innovative

- **Emotion-Driven Movement** – Jarvis physically responds to your emotions in real-time.
- **Neural Pose Estimation** – Maps emotions to animation with a trained regression model.
- **Fully Modular System** – Swap any module independently (LLM, emotion model, TTS, etc).
- **Unity as Real-Time Renderer** – Brings 3D emotional response into a live environment.
- **Extensibility** – Adaptable to other avatars, robots, or platforms.

---

### 🔧 How It Was Made

- Most of the logic was written in **Python**, except for **Unity + C# scripts** for animation.
- The 3D robot character was built with [Spline](https://spline.design/) and rigged in **Blender**.
- A custom neural network was trained on **10,000 samples**, generated synthetically using LLMs + [CTGAN](https://sdv.dev/SDV/user_guides/single_table/ctgan.html).
- The Unity character bones were manually analyzed to set min/max rotation bounds for realism.

---

### 💥 Challenges Faced

- Real-time communication between Unity and Python (via Flask API)
- Ensuring natural motion from sparse AVD values
- Avoiding glitches from malformed Unity rig data
- Keeping latency down despite using multiple AI modules (TTS, LLM, Whisper)
- Dealing with Unity rig deformation and axis misalignment

---

### 🧠 What I Learned

- Built and trained regression neural networks for pose generation
- Learned Unity and C# for real-time animation
- Understood the importance of modular AI pipelines
- Learned Blender rigging + Unity bone mapping for animation systems
- Developed emotion modeling with AVD theory

---

### 🚀 Future Vision

- Add **voice command** to trigger physical actions (e.g. "Jarvis, wave")
- Expand the brain into **modular neural nets** (memory, planning, language, motor control)
- Port to **physical robotics** using Raspberry Pi + servo motors
- Add **vision systems** (OpenCV + YOLO) for visual awareness and gesture recognition
- Eventually create a **real-time humanoid companion AI**

---

## 🧪 Getting Started

### 1. Clone the Repo

git clone https://github.com/Daunting84/JARVIS_emotionally_intelligent_virtual_assistant.git
cd jarvis-ai

### 2. Activate the Server and Python code

be sure to run these files in this order
python flask_pose_server.py
python main.py

### 3. Set Up Unity (C# + 3D Model)
Unfortunately, the 3D model used for Jarvis could not be included in this repository. Due to file size and licensing, you’ll need to:

Create your own humanoid robot character using Blender, Mixamo, or Spline

Rig it properly with bones like: Head, Neck, LeftShoulder, etc.

Import it into Unity

Attach the included PoseUpdater.cs script

Make sure the character has Transform references assigned in the Inspector

If done correctly, your character should respond to real-time emotional cues via the Flask server.

