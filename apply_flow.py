import json
import os
from datetime import datetime

# File-based applications storage
APP_FILE = "applications.json"

def load_applications():
    if os.path.exists(APP_FILE):
        try:
            with open(APP_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            save_applications({})
            return {}
        except Exception as e:
            print(f"Error loading applications: {e}")
            return {}
    return {}

def save_applications(data):
    with open(APP_FILE, "w") as f:
        json.dump(data, f, indent=2)


def apply_to_job(job_id, user_id, resume_path):
    # File-based application
    data = load_applications()

    if job_id not in data:
        data[job_id] = {}

    if user_id in data[job_id]:
        return False  # already applied

    data[job_id][user_id] = {
        "resume": resume_path,
        "applied_at": datetime.now().isoformat(),
        "status": "Applied",
        "score": None
    }

    save_applications(data)
    return True
