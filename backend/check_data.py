from database import SessionLocal
import models

db = SessionLocal()
try:
    users = db.query(models.User).all()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"ID: {u.id} | Name: {u.name} | Role: {u.role}")
    
    profiles = db.query(models.Profile).all()
    print(f"\nTotal Profiles: {len(profiles)}")
    for p in profiles:
        print(f"ID: {p.id} | UserID: {p.user_id} | Status: {p.status}")

finally:
    db.close()
