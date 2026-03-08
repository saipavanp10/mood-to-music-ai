from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, get_db
import models
import model_handler
import datetime

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class MusicRecommendation(BaseModel):
    mood: str
    songs: list

# Helper for music logic (Rule-based)
def get_music_recommendation(mood: str):
    # Mock Database of Songs
    # Images are placeholders or generic album covers
    songs_db = {
        "happy": [
            {"title": "Happy", "artist": "Pharrell Williams", "image": "https://i.scdn.co/image/ab67616d0000b273295b263901b87a8f3317bd6e", "link": "https://open.spotify.com/track/60nZcImufyMA1SFQYocFij"},
            {"title": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "image": "https://i.scdn.co/image/ab67616d0000b273754b2fc7d230d74052e70335", "link": "https://open.spotify.com/track/1WkMMavIMc4JZ8cfMmxHkI"},
            {"title": "Uptown Funk", "artist": "Mark Ronson", "image": "https://i.scdn.co/image/ab67616d0000b273c52e12e160a22da259d604b7", "link": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"}
        ],
        "sad": [
            {"title": "Someone Like You", "artist": "Adele", "image": "https://i.scdn.co/image/ab67616d0000b273211839b2cfdb7a72d427771b", "link": "https://open.spotify.com/track/4kflIGfjkRGleCnnCa0Ks9"},
            {"title": "Fix You", "artist": "Coldplay", "image": "https://i.scdn.co/image/ab67616d0000b273030d939626e2e584f2762a5b", "link": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"},
            {"title": "The Night We Met", "artist": "Lord Huron", "image": "https://i.scdn.co/image/ab67616d0000b2730ba6f92025ed9960e6e73685", "link": "https://open.spotify.com/track/3hRV0jL3vUpRrcy398teAU"}
        ],
        "angry": [
            {"title": "Break Stuff", "artist": "Limp Bizkit", "image": "https://i.scdn.co/image/ab67616d0000b2730f40d890b0d342be390a3c26", "link": "https://open.spotify.com/track/5cZqsjVs6MevCnAkasbEOX"},
            {"title": "Killing In The Name", "artist": "Rage Against The Machine", "image": "https://i.scdn.co/image/ab67616d0000b273778a46761894d86c75775f0f", "link": "https://open.spotify.com/track/59WN2psjkt1tyaxjspN8fp"},
            {"title": "Numb", "artist": "Linkin Park", "image": "https://i.scdn.co/image/ab67616d0000b273eed1a9b407e78103c8c6913e", "link": "https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"}
        ],
        "neutral": [
            {"title": "Lo-Fi Beats", "artist": "Chill Lofi", "image": "https://i.scdn.co/image/ab67616d0000b273b06c641d017a151048695d75", "link": "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn"},
            {"title": "Weightless", "artist": "Marconi Union", "image": "https://i.scdn.co/image/ab67616d0000b2738b525281488665c711a3d922", "link": "https://open.spotify.com/track/6kKwZB2ii4ClfdQ25rCVv7"},
            {"title": "Sunset Lover", "artist": "Petit Biscuit", "image": "https://i.scdn.co/image/ab67616d0000b273bc5e26b86ce90623a31e8bfb", "link": "https://open.spotify.com/track/0hNduWmlWmEmuwEFcYvRu1"}
        ]
    }
    return songs_db.get(mood, songs_db["neutral"])

# API Endpoints
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # In real app, hash password!
    new_user = models.User(username=user.username, hashed_password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.hashed_password != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"id": db_user.id, "username": db_user.username}

@app.post("/analyze")
async def analyze_mood(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    
    # Run heavy AI
    mood = model_handler.model.predict_emotion(contents)
    
    # Get Music List (Rich Data)
    music_list = get_music_recommendation(mood)
    
    # Save to History
    # We'll save the first song's link or just the mood for simplicity in DB for now
    # Or strict string representation
    first_song = music_list[0]['link'] if music_list else ""
    
    new_entry = models.History(
        user_id=user_id,
        mood=mood,
        song_recommended=first_song,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_entry)
    db.commit()
    
    return {"mood": mood, "songs": music_list}

@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(models.History).filter(models.History.user_id == user_id).order_by(models.History.timestamp.desc()).all()
    return history
