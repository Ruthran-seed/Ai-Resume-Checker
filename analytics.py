import json
import os
from collections import Counter

APP_FILE = "applications.json"
JOB_FILE = "jobs.json"


# ---------- LOADERS ----------
def load_applications():
    if os.path.exists(APP_FILE):
        with open(APP_FILE, "r") as f:
            return json.load(f)
    return {}


def load_jobs():
    if os.path.exists(JOB_FILE):
        with open(JOB_FILE, "r") as f:
            return json.load(f)
    return {}


# ---------- BASIC COUNTS ----------
def total_applications():
    data = load_applications()
    return sum(len(users) for users in data.values())


def applications_per_job():
    data = load_applications()
    return {job_id: len(users) for job_id, users in data.items()}


# ---------- STATUS ANALYTICS ----------
def status_distribution(job_id=None):
    """
    Returns count of each status.
    If job_id is None → overall stats
    """
    data = load_applications()
    counter = Counter()

    for j_id, users in data.items():
        if job_id and j_id != job_id:
            continue
        for info in users.values():
            counter[info.get("status", "Applied")] += 1

    return dict(counter)


# ---------- SCORE ANALYTICS ----------
def score_stats(job_id):
    """
    Returns min, max, avg score for a job
    """
    data = load_applications()
    scores = []

    for info in data.get(job_id, {}).values():
        if info.get("score") is not None:
            scores.append(info["score"])

    if not scores:
        return {
            "min": 0,
            "max": 0,
            "avg": 0
        }

    return {
        "min": min(scores),
        "max": max(scores),
        "avg": round(sum(scores) / len(scores), 2)
    }


# ---------- TOP CANDIDATES ----------
def top_candidates(job_id, top_n=5):
    """
    Returns top N candidates sorted by score
    """
    data = load_applications()
    candidates = []

    for user_id, info in data.get(job_id, {}).items():
        if info.get("score") is not None:
            candidates.append({
                "user_id": user_id,
                "score": info["score"],
                "status": info.get("status", "Applied"),
                "applied_at": info.get("applied_at")
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]


# ---------- SKILL GAP (BASIC) ----------
def skill_gap_analysis(job_keywords, resume_texts):
    """
    Compare job keywords with resume words
    Returns missing skills
    """
    job_set = set(k.lower() for k in job_keywords)
    resume_words = set()

    for text in resume_texts:
        resume_words.update(text.lower().split())

    missing = job_set - resume_words
    return list(missing)
