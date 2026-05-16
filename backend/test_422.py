import requests
from fastapi.testclient import TestClient
import sys
import os

# add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

client = TestClient(app)

# Create a test user
test_user = {
    "name": "Test User",
    "email": "test422@example.com",
    "password": "password123",
    "role": "candidate"
}

client.post("/api/auth/register", json=test_user)

# Login
resp = client.post("/api/auth/login", json={"email": "test422@example.com", "password": "password123"})
token = resp.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

payload = {
    "job_title": "Professional",
    "phone": "",
    "contact_email": "",
    "summary": "",
    "skills": ["Python", "AWS"],
    "education": [],
    "experience": [],
    "courses": [],
    "projects": []
}

resp = client.put("/api/profile/me", json=payload, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.json())
