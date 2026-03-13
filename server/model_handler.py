from deepface import DeepFace
import cv2
import numpy as np
import base64

class EmotionModel:
    def __init__(self):
        print("Loading DeepFace model... (Lazy loaded on first call usually)")

    def predict_emotion(self, image_bytes):
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # DeepFace analysis
            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            
            if isinstance(result, list):
                result = result[0]
            
            dominant   = result['dominant_emotion']
            all_scores = result['emotion']  # dict {emotion: numpy.float32}

            # ⚠️ Convert numpy.float32 → plain Python float for JSON serialization
            all_scores_clean = {k: round(float(v), 2) for k, v in all_scores.items()}
            confidence       = round(float(all_scores_clean.get(dominant, 0.0)), 2)

            return dominant, confidence, all_scores_clean
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return "neutral", 50.0, {}  # Fallback


model = EmotionModel()
