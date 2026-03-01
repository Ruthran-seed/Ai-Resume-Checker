import json
import os

APP_FILE = "applications.json"

def update_score(job_id, user_id, score):
    try:
        with open(APP_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return False
            data = json.loads(content)

        if job_id not in data or user_id not in data[job_id]:
            return False
            
        data[job_id][user_id]["score"] = score

        with open(APP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error updating score: {e}")
        return False
