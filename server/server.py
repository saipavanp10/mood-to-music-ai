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

    songs_db = {
        "happy": [
            {
                "title": "Happy",
                "artist": "Pharrell Williams",
                "link": "https://open.spotify.com/search/happy%20pharrell%20williams"
            },
            {
                "title": "Can't Stop the Feeling!",
                "artist": "Justin Timberlake",
                "link": "https://open.spotify.com/search/cant%20stop%20the%20feeling%20justin%20timberlake"
            },
            {
                "title": "Uptown Funk",
                "artist": "Mark Ronson ft. Bruno Mars",
                "link": "https://open.spotify.com/search/uptown%20funk%20mark%20ronson%20bruno%20mars"
            }
        ],

        "sad": [
            {
                "title": "Someone Like You",
                "artist": "Adele",
                "link": "https://open.spotify.com/search/someone%20like%20you%20adele"
            },
            {
                "title": "Fix You",
                "artist": "Coldplay",
                "link": "https://open.spotify.com/search/fix%20you%20coldplay"
            },
            {
                "title": "The Night We Met",
                "artist": "Lord Huron",
                "link": "https://open.spotify.com/search/the%20night%20we%20met%20lord%20huron"
            }
        ],

        "angry": [
            {
                "title": "Break Stuff",
                "artist": "Limp Bizkit",
                "link": "https://open.spotify.com/search/break%20stuff%20limp%20bizkit"
            },
            {
                "title": "Killing In The Name",
                "artist": "Rage Against The Machine",
                "link": "https://open.spotify.com/search/killing%20in%20the%20name%20rage%20against%20the%20machine"
            },
            {
                "title": "Numb",
                "artist": "Linkin Park",
                "link": "https://open.spotify.com/search/numb%20linkin%20park"
            }
        ],

        "neutral": [
            {
                "title": "Lo-Fi Beats",
                "artist": "Chill Lofi",
                "link": "https://open.spotify.com/search/lofi%20beats"
            },
            {
                "title": "Weightless",
                "artist": "Marconi Union",
                "link": "https://open.spotify.com/search/weightless%20marconi%20union"
            },
            {
                "title": "Sunset Lover",
                "artist": "Petit Biscuit",
                "link": "https://open.spotify.com/search/sunset%20lover%20petit%20biscuit"
            }
        ],

        "fear": [
            {
                "title": "In the Air Tonight",
                "artist": "Phil Collins",
                "link": "https://open.spotify.com/search/in%20the%20air%20tonight%20phil%20collins"
            },
            {
                "title": "Thriller",
                "artist": "Michael Jackson",
                "link": "https://open.spotify.com/search/thriller%20michael%20jackson"
            },
            {
                "title": "People Are Strange",
                "artist": "The Doors",
                "link": "https://open.spotify.com/search/people%20are%20strange%20the%20doors"
            }
        ],

        "disgust": [
            {
                "title": "Creep",
                "artist": "Radiohead",
                "link": "https://open.spotify.com/search/creep%20radiohead"
            },
            {
                "title": "Boulevard of Broken Dreams",
                "artist": "Green Day",
                "link": "https://open.spotify.com/search/boulevard%20of%20broken%20dreams%20green%20day"
            },
            {
                "title": "Losing My Religion",
                "artist": "R.E.M.",
                "link": "https://open.spotify.com/search/losing%20my%20religion%20rem"
            }
        ],

        "surprise": [
            {
                "title": "Blinding Lights",
                "artist": "The Weeknd",
                "link": "https://open.spotify.com/search/blinding%20lights%20the%20weeknd"
            },
            {
                "title": "Don't Stop Me Now",
                "artist": "Queen",
                "link": "https://open.spotify.com/search/dont%20stop%20me%20now%20queen"
            },
            {
                "title": "Jump",
                "artist": "Van Halen",
                "link": "https://open.spotify.com/search/jump%20van%20halen"
            }
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
    
    return {
        "id": db_user.id, 
        "username": db_user.username,
        "is_admin": bool(db_user.is_admin)
    }

@app.get("/admin/history")
def get_all_history(db: Session = Depends(get_db)):
    # Fetch all history joined with username
    histories = db.query(models.History).order_by(models.History.timestamp.desc()).all()
    result = []
    for h in histories:
        # Avoid N+1 query issue in a real app, but fine for scale
        user = db.query(models.User).filter(models.User.id == h.user_id).first()
        if user:
            result.append({
                "id": h.id,
                "username": user.username,
                "mood": h.mood,
                "song_recommended": h.song_recommended,
                "timestamp": h.timestamp
            })
    return result

@app.post("/analyze")
async def analyze_mood(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    
    # Run heavy AI — returns (mood, confidence%, all_scores)
    mood, confidence, all_scores = model_handler.model.predict_emotion(contents)
    
    # Get Music List
    music_list = get_music_recommendation(mood)
    
    # Save to History
    first_song = music_list[0]['link'] if music_list else ""
    
    new_entry = models.History(
        user_id=user_id,
        mood=mood,
        song_recommended=first_song,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_entry)
    db.commit()
    
    return {
        "mood": mood,
        "confidence": confidence,       # e.g. 87.4
        "all_scores": all_scores,       # all 7 emotion %
        "songs": music_list
    }


@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(models.History).filter(models.History.user_id == user_id).order_by(models.History.timestamp.desc()).all()
    return history

@app.delete("/history/{user_id}")
def clear_history(user_id: int, db: Session = Depends(get_db)):
    deleted = db.query(models.History).filter(models.History.user_id == user_id).delete()
    db.commit()
    return {"message": f"Cleared {deleted} history entries."}
