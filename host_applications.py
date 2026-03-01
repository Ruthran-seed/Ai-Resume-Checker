import json
import os

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
            print(f"Warning: {APP_FILE} is corrupted")
            return {}
        except Exception as e:
            print(f"Error loading applications: {e}")
            return {}
    return {}

def get_applications_by_job(job_id):
    data = load_applications()
    return data.get(job_id, {})
