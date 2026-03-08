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
            # enforce_detection=False allows it to guess even if face is partial
            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            
            # Result is a list of dicts or a dict
            if isinstance(result, list):
                result = result[0]
            
            return result['dominant_emotion']
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return "neutral" # Fallback

model = EmotionModel()
