<div align="center">

# 🎵 Mood to Music AI

### *Your face. Your mood. Your music.*

An AI-powered full-stack web application that detects your **real-time facial emotion** via webcam and instantly generates a **personalized music playlist** to match your vibe.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vite](https://img.shields.io/badge/Frontend-Vite-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev/)
[![DeepFace](https://img.shields.io/badge/AI-DeepFace-FF6F00?style=for-the-badge&logo=tensorflow)](https://github.com/serengil/deepface)
[![Deployed on Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com)
[![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel)](https://vercel.com)

</div>

---

## 🧠 What It Does

Mood to Music uses **computer vision + deep learning** to read your facial expression through your webcam, classify your emotion into one of **7 categories**, and instantly serve you a curated Spotify playlist tailored to exactly how you feel — all in real time, right in the browser.

No manual input. No genre selection. Just you, your face, and music that *gets* you.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎭 **7-Emotion Detection** | Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral |
| 📷 **Camera Toggle** | Full privacy control — camera is OFF by default, you choose when to enable |
| 🎯 **Confidence Score** | Animated score bar showing how confident the AI is in its prediction |
| 📊 **All-Emotion Breakdown** | Mini bar chart showing every emotion's probability score |
| 🎵 **Personalized Playlists** | 3 curated Spotify-linked songs per detected emotion |
| 📈 **Model Metrics Tab** | Live Chart.js charts — accuracy, AUC, confusion matrix, training curves |
| 🗑️ **Clear History** | Delete your mood history with a custom confirmation modal |
| 👑 **Admin Dashboard** | View global mood usage across all users |
| 🔐 **Auth System** | Register & login with user session management |
| 🕓 **History Tracking** | Every analysis is logged with timestamp in local timezone |

---

## 🏗️ System Architecture

```
Webcam Input (Toggle On/Off)
        │
        ▼
Face Detection & Preprocessing (Resize 224×224, Normalize)
        │
        ▼
DeepFace CNN (VGG-Face Backbone, FER-2013 fine-tuned)
        │
        ▼
7-Class Emotion Classification + Confidence Scores
        │
   ┌────┴────┐
   │         │
   ▼         ▼
Grad-CAM   Music Recommendation Engine
Heatmap    (Rule-based mood → playlist mapping)
           │
           ▼
    Spotify Song Cards
           │
           ▼
    SQLite History DB  ←→  Clear History API
```

---

## 🤖 Model Performance

Evaluated on the **FER-2013 private test set** (3,589 images, 7 classes):

| Metric | Value |
|---|---|
| **Overall Accuracy** | 63.4% |
| **Average AUC** | 0.882 |
| **Best Class** | Happy (85.5% accuracy, AUC 0.976) |
| **Hardest Class** | Disgust (40.3% accuracy, AUC 0.864) |
| **CNN Backbone** | VGG-Face (Transfer Learning) |
| **Dataset** | FER-2013 (35,887 images, 7 emotions) |

> 📊 All metrics are displayed **live inside the app** in the Model Metrics tab with interactive Chart.js charts.

---

## 🛠️ Tech Stack

### Frontend
- **Vite** — blazing fast dev server & bundler
- **Vanilla JS + HTML + CSS** — glassmorphism UI with animations
- **Chart.js** — live accuracy, AUC, loss curves & confusion matrix
- **WebRTC** — webcam stream capture

### Backend
- **FastAPI** — async Python REST API
- **DeepFace** — Facebook's pre-trained facial emotion recognition model
- **OpenCV** — image preprocessing
- **SQLAlchemy + SQLite** — user auth & history database
- **Uvicorn** — ASGI server

### Deployment
- **Vercel** — frontend hosting (CDN, auto-deploy from GitHub)
- **Render** — backend hosting (free tier, auto-deploy from GitHub)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/saipavanp10/mood-to-music-ai.git
cd mood-to-music-ai
```

### 2. Start the Backend
```bash
cd server
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```
Backend runs at → `http://localhost:8000`
API docs at → `http://localhost:8000/docs`

### 3. Start the Frontend
```bash
cd client
npm install
npm run dev
```
Frontend runs at → `http://localhost:5173`

---

## 📁 Project Structure

```
mood-to-music-ai/
├── client/                  # Vite Frontend
│   ├── index.html           # Main HTML + Chart.js + Modal
│   ├── main.js              # App logic, charts, webcam, history
│   ├── api.js               # API client (auto-switches dev/prod URL)
│   └── style.css            # Glassmorphism design system
│
├── server/                  # FastAPI Backend
│   ├── server.py            # API routes (auth, analyze, history)
│   ├── model_handler.py     # DeepFace wrapper (returns confidence scores)
│   ├── models.py            # SQLAlchemy DB models
│   ├── database.py          # DB connection/session
│   ├── seed.py              # Admin user seeder
│   └── requirements.txt     # Python dependencies
│
├── render.yaml              # Render deployment config
└── README.md
```

---

## 🎭 Supported Emotions & Playlists

| Emotion | Sample Songs |
|---|---|
| 😄 Happy | Happy – Pharrell, Can't Stop the Feeling – JT, Uptown Funk |
| 😢 Sad | Someone Like You – Adele, Fix You – Coldplay |
| 😠 Angry | Break Stuff – Limp Bizkit, Numb – Linkin Park |
| 😐 Neutral | Lo-Fi Beats, Weightless – Marconi Union |
| 😨 Fear | Thriller – MJ, In the Air Tonight – Phil Collins |
| 🤢 Disgust | Creep – Radiohead, Boulevard of Broken Dreams – Green Day |
| 😲 Surprise | Blinding Lights – The Weeknd, Don't Stop Me Now – Queen |

---

## 📜 License

MIT License — feel free to fork, use, and build on this project.

---

<div align="center">

Built with ❤️ using DeepFace, FastAPI & Vite

⭐ Star this repo if you found it useful!

</div>
