# Assistive Technology – GestureTalk

## 🚀 Overview

GestureTalk is a real-time gesture-to-speech system that converts hand gestures into spoken phrases using computer vision and AI. It is designed to assist individuals with speech impairments by enabling seamless communication in everyday environments.

## ❗ Problem Statement

People with speech or hearing impairments often struggle with real-time communication in places like hospitals, cafes, and colleges. Existing solutions are either expensive or not intuitive. This project provides a low-cost, real-time alternative using only a camera and AI-based hand tracking.

---

## 🛠️ Tech Stack

* Python
* Flask
* OpenCV
* MediaPipe
* NumPy
* pyttsx3
* HTML, CSS, JavaScript

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv311
venv311\Scripts\activate
```

### 2. Fix MediaPipe Compatibility

MediaPipe may not support the latest Python versions.

👉 Use:

* Python **3.10 or 3.11**

Check:

```bash
python --version
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the App

```bash
python app.py
```

Open in browser:

```
http://localhost:5000
```

---

## 📂 Project Structure

```
app.py
camera.py
gestures.py
tts.py
config.py
templates/
static/
requirements.txt
```

---

## 💡 Features

* Real-time hand gesture recognition
* Context-based phrase mapping (cafe, hospital, etc.)
* Text-to-speech output
* Custom gesture training
* Live dashboard with status updates

---

## 🔧 Git Fix (Learning Highlight)

Large files (like virtual environments) were accidentally pushed and later removed by:

```bash
rmdir /s /q .git
git init
git branch -M main

echo venv311/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo *.pyd >> .gitignore
echo *.dll >> .gitignore

git add .
git commit -m "Clean project upload"
git remote add origin https://github.com/Blueundead24/Assistive-technology.git
git push -u origin main --force
```

---

## 🎯 Future Improvements

* Mobile application version
* Multi-language speech support
* Pre-trained gesture dataset
* Cloud deployment
