import json
import os
from datetime import datetime

NOTIF_FILE = "notifications.json"


# ---------- HELPERS ----------
def _load_notifications():
    if os.path.exists(NOTIF_FILE):
        with open(NOTIF_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_notifications(data):
    with open(NOTIF_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- CREATE NOTIFICATION ----------
def create_notification(user_id, title, message):
    """
    Save a notification for a user.
    """
    data = _load_notifications()

    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "title": title,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })

    _save_notifications(data)


# ---------- READ NOTIFICATIONS ----------
def get_notifications(user_id):
    """
    Get all notifications for a user.
    """
    data = _load_notifications()
    return data.get(user_id, [])


# ---------- MARK AS READ ----------
def mark_all_as_read(user_id):
    data = _load_notifications()

    if user_id in data:
        for n in data[user_id]:
            n["read"] = True

    _save_notifications(data)


# ---------- TRIGGER ON STATUS CHANGE ----------
def notify_status_change(user_id, job_id, new_status):
    """
    Call this when host updates application status.
    """
    title = "Application Status Updated"
    message = f"Your application for Job {job_id} is now marked as '{new_status}'."

    create_notification(user_id, title, message)
