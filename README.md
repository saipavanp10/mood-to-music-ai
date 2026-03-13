# Mood to Music

I built this project because I wanted to see if a webcam and some AI could actually understand how you're feeling — and then play music that fits. Turns out, it works pretty well.

The app opens your camera, looks at your face, figures out your emotion, and pulls up songs that match. No typing, no selecting genres, just point your face at the screen and hit analyze.

---

## How it works

The frontend captures a frame from your webcam and sends it to a FastAPI backend. The backend runs it through DeepFace (which uses a VGG-Face CNN model trained on FER-2013) to detect your dominant emotion. It also returns a confidence score so you can see how sure the model is. That emotion then maps to a small playlist of songs, which gets sent back and displayed.

Everything is logged to a SQLite database so you can see your mood history over time. There's also an admin view to see usage across all users.

---

## Emotions it detects

- Happy
- Sad
- Angry
- Neutral
- Fear
- Disgust
- Surprise

Each emotion has 3 songs mapped to it. The mapping is rule-based — I picked songs that I think fit each mood.

---

## Model accuracy

The model is DeepFace running on FER-2013. I didn't train it from scratch, it's a pre-trained model used for inference. On the FER-2013 test set it gets around 63.4% overall accuracy. Happy is the easiest to detect (around 85%), disgust is the hardest (around 40%) which makes sense since it's a subtle expression. AUC scores range from 0.82 to 0.97 across classes.

There's a metrics tab in the app that shows all this with charts — accuracy bars, AUC per class, training/validation curves, and a confusion matrix.

---

## Stack

**Frontend** — Vite, vanilla JS, CSS with a glassmorphism style, Chart.js for the metrics charts

**Backend** — FastAPI, DeepFace, OpenCV, SQLAlchemy with SQLite

**Deployed on** — Vercel (frontend) and Render (backend)

---

## Running it locally

Clone the repo, then start both servers:

```bash
# Backend
cd server
pip install -r requirements.txt
uvicorn server:app --reload --port 8000

# Frontend (new terminal)
cd client
npm install
npm run dev
```

Frontend → http://localhost:5173  
Backend → http://localhost:8000  
API docs → http://localhost:8000/docs

---

## Project structure

```
mood-to-music-ai/
├── client/
│   ├── index.html       # structure and tabs
│   ├── main.js          # all the frontend logic
│   ├── api.js           # API calls
│   └── style.css        # styling
│
└── server/
    ├── server.py        # API routes
    ├── model_handler.py # DeepFace wrapper
    ├── models.py        # database models
    ├── database.py      # DB setup
    └── requirements.txt
```

---

## A few things to note

The free tier on Render goes to sleep after inactivity, so the first request after a while might take 30–60 seconds to wake up. After that it's fine.

The model runs on CPU which means analysis takes a few seconds — it's not instant. If you're running it locally on a machine without a GPU, expect 3–8 seconds per analysis.

The camera is off by default. You have to click "Turn On Camera" yourself — I didn't want it to just start recording the moment the page loads.
