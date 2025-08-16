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
    except json.JSONDecodeError:
        rais