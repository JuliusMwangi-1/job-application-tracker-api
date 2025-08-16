from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import os
from typing import List

app = FastAPI(title="Job Application Tracker API")
security = HTTPBasic()

USERS_FILE = "users.json"
APPLICATIONS_FILE = "applications.json"

# ---------- Helper Functions ----------
def load_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except:
        raise HTTPException(status_code=500, detail=f"Error writing to {file}")

def authenticate(credentials: HTTPBasicCredentials):
    users = load_json(USERS_FILE)
    if credentials.username not in users or users[credentials.username]["password"] != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return users[credentials.username]

# ---------- Routes ----------
@app.post("/applications/")
def add_application(job_title: str, company: str, date_applied: str, status: str, user: dict = Depends(authenticate)):
    applications = load_json(APPLICATIONS_FILE)
    username = user["username"]
    if username not in applications:
        applications[username] = []
    applications[username].append({
        "job_title": job_title,
        "company": company,
        "date_applied": date_applied,
        "status": status
    })
    save_json(APPLICATIONS_FILE, applications)
    return {"message": "Application added successfully"}

@app.get("/applications/")
def get_applications(user: dict = Depends(authenticate)):
    applications = load_json(APPLICATIONS_FILE)
    username = user["username"]
    user_apps = applications.get(username, [])
    return {"applications": user_apps}
