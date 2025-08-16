from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import os

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
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error decoding {file}")
    except Exception:
        raise HTTPException(status_code=500, detail=f"Error reading {file}")

def save_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        raise HTTPException(status_code=500, detail=f"Error writing to {file}")

def authenticate(credentials: HTTPBasicCredentials):
    users = load_json(USERS_FILE)
    if credentials.username not in users or users[credentials.username]["password"] != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return users[credentials.username]

# ---------- Routes ----------
@app.post("/applications/")
def add_application(job_title: str, company: str, date_applied: str, status: str, user: dict = Depends(authenticate)):
    try:
        if not job_title or not company or not date_applied or not status:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        applications = load_json(APPLICATIONS_FILE)
        username = user["username"]
        if username not in applications:
            applications[username] = []
        
        new_app = {
            "job_title": job_title,
            "company": company,
            "date_applied": date_applied,
            "status": status
        }
        applications[username].append(new_app)
        save_json(APPLICATIONS_FILE, applications)
        
        return {"message": "Application added successfully", "application": new_app}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while adding application")

@app.get("/applications/")
def get_applications(user: dict = Depends(authenticate)):
    try:
        applications = load_json(APPLICATIONS_FILE)
        username = user["username"]
        user_apps = applications.get(username, [])
        return {"username": username, "applications": user_apps}
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while fetching applications")
