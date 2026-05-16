from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE profiles ADD COLUMN contact_email VARCHAR(150);'))
        print("Added contact_email")
    except Exception as e:
        print(e)
    try:
        conn.execute(text('ALTER TABLE profiles ADD COLUMN summary TEXT;'))
        print("Added summary")
    except Exception as e:
        print(e)
    conn.commit()

