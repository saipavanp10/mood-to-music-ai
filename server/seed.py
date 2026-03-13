from database import SessionLocal, engine
import models

# Ensure tables exist (Recreate them to apply schema changes)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

def seed_users():
    db = SessionLocal()
    try:
        sample_users = [
            {"username": "testuser", "password": "password123", "is_admin": 0},
            {"username": "demouser", "password": "demo123", "is_admin": 0},
            {"username": "admin", "password": "admin", "is_admin": 1}
        ]
        
        added = 0
        for user_data in sample_users:
            # Check if exists
            existing = db.query(models.User).filter(models.User.username == user_data['username']).first()
            if not existing:
                new_user = models.User(
                    username=user_data['username'], 
                    hashed_password=user_data['password'],
                    is_admin=user_data.get('is_admin', 0)
                )
                db.add(new_user)
                added += 1
                print(f"Added user: {user_data['username']} with password: {user_data['password']}")
            else:
                print(f"User {user_data['username']} already exists.")
        
        if added > 0:
            db.commit()
            print(f"Successfully added {added} sample users.")
        else:
            print("No new users added.")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
