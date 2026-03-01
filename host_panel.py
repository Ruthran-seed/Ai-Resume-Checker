import streamlit as st
import json
import os
import time
import csv
from io import StringIO
from datetime import datetime, timedelta

from host_applications import get_applications_by_job
from resume_parser import extract_text_from_pdf
from ai_matching import calculate_match_score
from score_updater import update_score
from status_updater import update_status
from host_chat import host_chat_interface

# ---------------- FILE PATHS ----------------
JOB_FILE = "jobs.json"
USER_FILE = "users.json"
APP_FILE = "applications.json"
HOST_ACTIVITY_FILE = "host_activity_log.json"
HOST_ROLES_FILE = "host_roles.json"

# ---------------- HELPERS ----------------
def load_jobs():
    if os.path.exists(JOB_FILE):
        try:
            with open(JOB_FILE, "r") as f:
                content = f.read().strip()
                if not content:  # Handle empty file
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            # File is corrupted, reinitialize it
            print(f"Warning: {JOB_FILE} is corrupted, resetting to empty dict")
            save_jobs({})
            return {}
        except Exception as e:
            print(f"Error loading jobs: {e}")
            return {}
    return {}

def save_jobs(jobs):
    with open(JOB_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                content = f.read().strip()
                if not content:  # Handle empty file
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            # File is corrupted, reinitialize it
            print(f"Warning: {USER_FILE} is corrupted, resetting to empty dict")
            return {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    return {}

def generate_job_id():
    import random
    return "JOB" + str(random.randint(1000, 9999))

def create_job_entry(title, location, description, keywords):
    """Create a new job posting"""
    job_id = generate_job_id()
    while job_id in load_jobs():
        job_id = generate_job_id()
    
    jobs = load_jobs()
    jobs[job_id] = {
        "title": title,
        "location": location,
        "description": description,
        "keywords": keywords.split(",") if isinstance(keywords, str) else keywords,
        "created_at": str(__import__('datetime').datetime.now())
    }
    save_jobs(jobs)
    return job_id

def load_applications_data():
    if os.path.exists(APP_FILE):
        try:
            with open(APP_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception:
            return {}
    return {}

def save_applications_data(data):
    with open(APP_FILE, "w") as f:
        json.dump(data, f, indent=2)

def parse_dt(dt_text):
    if not dt_text:
        return None
    try:
        return datetime.fromisoformat(str(dt_text).replace("Z", ""))
    except Exception:
        return None

def load_host_roles():
    if os.path.exists(HOST_ROLES_FILE):
        try:
            with open(HOST_ROLES_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception:
            return {}
    return {}

def save_host_roles(data):
    with open(HOST_ROLES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_host_role(host_id):
    roles = load_host_roles()
    if host_id not in roles:
        roles[host_id] = "admin"
        save_host_roles(roles)
    return roles.get(host_id, "viewer")

def set_host_role(host_id, role):
    roles = load_host_roles()
    roles[host_id] = role
    save_host_roles(roles)

def load_activity_log():
    if os.path.exists(HOST_ACTIVITY_FILE):
        try:
            with open(HOST_ACTIVITY_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception:
            return []
    return []

def save_activity_log(logs):
    with open(HOST_ACTIVITY_FILE, "w") as f:
        json.dump(logs[-400:], f, indent=2)

def add_activity(actor_id, action, details):
    logs = load_activity_log()
    logs.append({
        "at": datetime.now().isoformat(),
        "actor": actor_id,
        "action": action,
        "details": details
    })
    save_activity_log(logs)

def update_application_status_with_log(job_id, user_id, new_status, actor_id):
    data = load_applications_data()
    if job_id not in data or user_id not in data[job_id]:
        return False
    old_status = data[job_id][user_id].get("status", "Applied")
    data[job_id][user_id]["status"] = new_status
    if new_status == "Hired":
        data[job_id][user_id]["hired_at"] = datetime.now().isoformat()
    save_applications_data(data)
    if old_status != new_status:
        add_activity(actor_id, "status_update", f"{job_id}:{user_id} {old_status} -> {new_status}")
    return True

def calculate_kpis(jobs, applications_data):
    total_jobs = len(jobs)
    all_apps = []
    for jid, applicants in applications_data.items():
        for uid, info in applicants.items():
            all_apps.append((jid, uid, info))

    total_apps = len(all_apps)
    active_apps = sum(1 for _, _, info in all_apps if info.get("status") not in ["Rejected", "Hired"])
    interview_count = sum(1 for _, _, info in all_apps if info.get("status") in ["Interview", "Offer", "Hired"])
    hired_count = sum(1 for _, _, info in all_apps if info.get("status") == "Hired")
    interview_rate = (interview_count / total_apps * 100) if total_apps else 0
    hire_rate = (hired_count / total_apps * 100) if total_apps else 0

    hire_days = []
    for _, _, info in all_apps:
        if info.get("status") == "Hired":
            applied_dt = parse_dt(info.get("applied_at"))
            hired_dt = parse_dt(info.get("hired_at"))
            if applied_dt and hired_dt and hired_dt >= applied_dt:
                hire_days.append((hired_dt - applied_dt).days)
    avg_time_to_hire = (sum(hire_days) / len(hire_days)) if hire_days else 0

    stale_cutoff = datetime.now() - timedelta(days=7)
    pending_actions = 0
    for _, _, info in all_apps:
        applied_dt = parse_dt(info.get("applied_at"))
        status = info.get("status", "Applied")
        if (info.get("score") is None) or (applied_dt and applied_dt < stale_cutoff and status in ["Applied", "Under Review"]):
            pending_actions += 1

    return {
        "total_jobs": total_jobs,
        "total_apps": total_apps,
        "active_apps": active_apps,
        "interview_rate": interview_rate,
        "hire_rate": hire_rate,
        "avg_time_to_hire": avg_time_to_hire,
        "pending_actions": pending_actions
    }

# ---------------- HOST DASHBOARD ----------------
def host_dashboard():
    
    # Initialize host_page if not exists
    if "host_page" not in st.session_state:
        st.session_state.host_page = "main"

    current_host_id = st.session_state.get("current_host_id") or "host_admin"
    current_role = get_host_role(current_host_id)
    can_manage_jobs = current_role in ["admin", "recruiter"]
    is_admin = current_role == "admin"
    
    # -------- CREATE JOB PAGE --------
    if st.session_state.host_page == "create_job":
        if not can_manage_jobs:
            st.error("❌ Permission denied. Only Admin/Recruiter can create jobs.")
            if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_create_job_denied"):
                st.session_state.host_page = "main"
                st.rerun()
            return
        st.markdown("<h2 style='color:#A8D5BA;'>➕ Create New Job</h2>", unsafe_allow_html=True)
        with st.form("create_job_form"):
            title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
            location = st.text_input("Location", placeholder="e.g., New York, NY")
            description = st.text_area("Job Description", placeholder="Enter detailed job description", height=120)
            keywords = st.text_input("Keywords (comma-separated)", placeholder="e.g., Python, Django, REST API")
            
            submit = st.form_submit_button("Post Job", use_container_width=True)
            if submit:
                if not title or not location or not description:
                    st.error("❌ Please fill all required fields")
                else:
                    with st.spinner("📝 Creating job posting..."):
                        job_id = create_job_entry(title, location, description, keywords)
                        add_activity(current_host_id, "job_created", f"Created {job_id} - {title}")
                        time.sleep(0.5)
                    st.success(f"✅ Job posted successfully! Job ID: {job_id}")
                    st.session_state.host_page = "main"
                    st.rerun()
        
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_create_job"):
            st.session_state.host_page = "main"
            st.rerun()
        return
    
    # -------- VIEW USERS PAGE --------
    if st.session_state.host_page == "view_users":
        st.markdown("<h2 style='color:#A8D5BA;'>👥 User Profiles</h2>", unsafe_allow_html=True)
        users = load_users()
        
        if not users:
            st.info("📭 No users found in the system")
        else:
            st.write(f"Total Users: **{len(users)}**")
            st.markdown("---")
            
            for user_id, user_data in users.items():
                with st.expander(f"👤 {user_data.get('email', 'N/A')} ({user_id})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        avatar_path = user_data.get("profile", {}).get("avatar")
                        if avatar_path and os.path.exists(avatar_path):
                            st.image(avatar_path, width=120)
                        elif avatar_path:
                            st.warning(f"⚠️ Avatar file not found: {avatar_path}")
                    with col2:
                        st.write(f"**Name:** {user_data.get('profile', {}).get('name', 'N/A')}")
                        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
                        st.write(f"**Phone:** {user_data.get('profile', {}).get('phone', 'N/A')}")
                        st.write(f"**City:** {user_data.get('profile', {}).get('city', 'N/A')}")
                    
                    st.write(f"**Qualification:** {user_data.get('profile', {}).get('qualification', 'N/A')}")
                    skills = user_data.get('profile', {}).get('skills', [])
                    st.write(f"**Skills:** {', '.join(skills) if skills else 'N/A'}")
        
        st.markdown("---")
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_analyse_users"):
            st.session_state.host_page = "main"
            st.rerun()
        return
    
    # -------- ANALYSE ALL RESUMES PAGE --------
    if st.session_state.host_page == "analyse_all":
        st.markdown("<h2 style='color:#A8D5BA;'>🤖 Analyse All Resumes</h2>", unsafe_allow_html=True)
        
        jobs = load_jobs()
        if not jobs:
            st.warning("📋 No jobs found. Create a job first.")
        else:
            job_id = st.selectbox("Select Job", options=list(jobs.keys()), format_func=lambda x: f"{x} — {jobs[x]['title']}")
            
            if st.button("🚀 Analyse All Resumes for This Job", use_container_width=True, key="btn_analyse_resumes"):
                applications = get_applications_by_job(job_id)
                if not applications:
                    st.warning("📭 No applications for this job")
                else:
                    with st.spinner(f"🤖 Analyzing {len(applications)} resumes with AI..."):
                        st.info(f"🔄 Analysing {len(applications)} resumes...")
                        job_desc = jobs[job_id].get("description", "")
                        scores_updated = 0
                        
                        progress_bar = st.progress(0)
                        for idx, (user_id, info) in enumerate(applications.items()):
                            resume_path = info.get("resume")
                            if resume_path and os.path.exists(resume_path):
                                try:
                                    resume_text = extract_text_from_pdf(resume_path)
                                    score = calculate_match_score(resume_text, job_desc)
                                    update_score(job_id, user_id, score)
                                    scores_updated += 1
                                except Exception as e:
                                    st.warning(f"⚠️ Error processing {user_id}: {str(e)}")
                            
                            progress_bar.progress((idx + 1) / len(applications))
                        
                        time.sleep(0.5)
                    st.success(f"✅ Analysis complete! Updated {scores_updated}/{len(applications)} resumes")
        
        st.markdown("---")
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_analyse_all"):
            st.session_state.host_page = "main"
            st.rerun()
        return
    
    # -------- DELETE JOB PAGE --------
    if st.session_state.host_page == "delete_job":
        if not is_admin:
            st.error("❌ Permission denied. Only Admin can delete jobs.")
            if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_delete_job_denied"):
                st.session_state.host_page = "main"
                st.rerun()
            return
        st.markdown("<h2 style='color:#A8D5BA;'>🗑️ Delete Job Posting</h2>", unsafe_allow_html=True)
        
        jobs = load_jobs()
        if not jobs:
            st.warning("📋 No jobs found to delete")
        else:
            st.write("Select a job to delete:")
            job_id = st.selectbox("Job", options=list(jobs.keys()), format_func=lambda x: f"{x} — {jobs[x]['title']}", key="delete_job_selector")
            
            job_info = jobs[job_id]
            with st.expander(f"📋 Job Details", expanded=True):
                st.write(f"**Title:** {job_info.get('title')}")
                st.write(f"**Location:** {job_info.get('location')}")
                st.write(f"**Description:** {job_info.get('description')}")
                st.write(f"**Job ID:** {job_id}")
            
            st.warning("⚠️ This action cannot be undone. All applications for this job will remain in the system but linked to a deleted job.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirm Delete", use_container_width=True, key="btn_confirm_delete"):
                    with st.spinner("🗑️ Deleting job..."):
                        del jobs[job_id]
                        save_jobs(jobs)
                        add_activity(current_host_id, "job_deleted", f"Deleted {job_id}")
                        time.sleep(0.5)
                    st.success(f"✅ Job {job_id} has been deleted successfully")
                    st.balloons()
                    time.sleep(1)
                    st.session_state.host_page = "main"
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True, key="btn_cancel_delete"):
                    st.session_state.host_page = "main"
                    st.rerun()
        
        st.markdown("---")
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_delete_job"):
            st.session_state.host_page = "main"
            st.rerun()
        return


    
    # Add professional CSS styling for host panel
    st.markdown("""
    <style>
    .host-header {
        text-align: center;
        margin-bottom: 24px;
        padding: 20px;
        background: rgba(168, 213, 186, 0.08);
        border-radius: 12px;
        border-left: 4px solid #A8D5BA;
    }
    .job-selector-container {
        background: rgba(255,255,255,0.04);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .candidate-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(168,213,186,0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    .action-buttons {
        display: flex;
        gap: 12px;
        margin: 16px 0;
        flex-wrap: wrap;
    }
    .btn-primary {
        padding: 10px 16px;
        background-color: #1F6B4F;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        text-align: center;
    }
    .btn-primary:hover {
        background-color: #15593f;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31,107,79,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="host-header">
        <h2 style="color:#A8D5BA; margin:0;">👔 Host Control Panel</h2>
        <p style="color:#d7d7d7; margin:8px 0 0 0; font-size:14px;">Manage job postings, review candidates, and make hiring decisions</p>
        <p style="color:#B8D8FF; margin:8px 0 0 0; font-size:13px;">Host: <b>{current_host_id}</b> | Role: <b>{current_role.upper()}</b></p>
    </div>
    """, unsafe_allow_html=True)

    jobs = load_jobs()
    applications_data = load_applications_data()
    users = load_users()
    kpis = calculate_kpis(jobs, applications_data)

    if "resolved_alert_ids" not in st.session_state:
        st.session_state.resolved_alert_ids = []
    if "seen_top_match_keys" not in st.session_state:
        st.session_state.seen_top_match_keys = []

    st.markdown("<h4 style='color:#A8D5BA;'>Executive KPI Strip</h4>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.metric("Total Jobs", kpis["total_jobs"])
    with k2:
        st.metric("Active Applications", kpis["active_apps"])
    with k3:
        st.metric("Interview Rate", f"{kpis['interview_rate']:.1f}%")
    with k4:
        st.metric("Hire Rate", f"{kpis['hire_rate']:.1f}%")
    with k5:
        st.metric("Avg Time-to-Hire", f"{kpis['avg_time_to_hire']:.1f} days")
    with k6:
        st.metric("Pending Actions", kpis["pending_actions"])

    st.markdown("<h4 style='color:#A8D5BA;'>Smart Alerts</h4>", unsafe_allow_html=True)
    top_candidates = []
    stale_candidates = []
    stale_cutoff = datetime.now() - timedelta(days=7)
    zero_jobs = []
    aging_jobs = []

    for job_id, job_info in jobs.items():
        apps = applications_data.get(job_id, {})
        if not apps:
            zero_jobs.append((job_id, job_info.get("title", "Untitled")))

        created_dt = parse_dt(job_info.get("created_at"))
        if created_dt and (datetime.now() - created_dt).days >= 20 and len(apps) < 3:
            aging_jobs.append((job_id, job_info.get("title", "Untitled")))

        for user_id, info in apps.items():
            score = info.get("score")
            status = info.get("status", "Applied")
            applied_dt = parse_dt(info.get("applied_at"))
            if score is not None and score >= 80 and status in ["Applied", "Under Review", "Shortlisted"]:
                top_candidates.append((job_id, user_id, score))
            if applied_dt and applied_dt < stale_cutoff and status in ["Applied", "Under Review"]:
                stale_candidates.append((job_id, user_id, applied_dt.strftime("%Y-%m-%d")))

    top_candidates = sorted(top_candidates, key=lambda x: x[2], reverse=True)
    current_top_keys = [f"{jid}:{uid}" for jid, uid, _ in top_candidates]
    seen_top_keys = set(st.session_state.get("seen_top_match_keys", []))
    resolved_ids = set(st.session_state.get("resolved_alert_ids", []))

    alerts = []

    for job_id, user_id, score in top_candidates:
        top_key = f"{job_id}:{user_id}"
        if top_key not in seen_top_keys:
            alerts.append({
                "id": f"top:{top_key}",
                "type": "new_top_match",
                "severity": "success",
                "job_id": job_id,
                "user_id": user_id,
                "message": f"🚀 New top-match candidate: {user_id} scored {score}/100 for {job_id}",
                "preset": "High-score candidates"
            })

    if stale_candidates:
        alerts.append({
            "id": f"stale:{len(stale_candidates)}",
            "type": "stale_apps",
            "severity": "warning",
            "job_id": stale_candidates[0][0],
            "user_id": None,
            "message": f"⏳ Stale applications > 7 days: {len(stale_candidates)} candidate(s)",
            "preset": "Urgent roles"
        })

    if zero_jobs:
        alerts.append({
            "id": f"zero:{len(zero_jobs)}",
            "type": "zero_apps",
            "severity": "warning",
            "job_id": zero_jobs[0][0],
            "user_id": None,
            "message": "📭 Jobs with zero applicants: " + ", ".join([jid for jid, _ in zero_jobs[:4]]),
            "preset": "All"
        })

    if aging_jobs:
        alerts.append({
            "id": f"aging:{len(aging_jobs)}",
            "type": "deadline",
            "severity": "warning",
            "job_id": aging_jobs[0][0],
            "user_id": None,
            "message": "📅 Deadline reminders: aging jobs need attention: " + ", ".join([jid for jid, _ in aging_jobs[:4]]),
            "preset": "Urgent roles"
        })

    active_alerts = [a for a in alerts if a["id"] not in resolved_ids]

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Open Alerts", len(active_alerts))
    with s2:
        st.metric("Critical", sum(1 for a in active_alerts if a["severity"] in ["warning", "error"]))
    with s3:
        st.metric("New Top-Match", sum(1 for a in active_alerts if a["type"] == "new_top_match"))

    control_col1, control_col2 = st.columns([1, 1])
    with control_col1:
        if st.button("✅ Mark Top-Match as Seen", key="alerts_mark_seen", use_container_width=True):
            st.session_state.seen_top_match_keys = current_top_keys
            st.success("Top-match alerts marked as seen")
            st.rerun()
    with control_col2:
        if st.button("🧹 Clear Resolved Alerts", key="alerts_clear_resolved", use_container_width=True):
            st.session_state.resolved_alert_ids = []
            st.success("Resolved alerts cleared")
            st.rerun()

    if not active_alerts:
        st.success("✅ No active alerts right now")
    else:
        for idx, alert in enumerate(active_alerts):
            if alert["severity"] == "warning":
                st.warning(alert["message"])
            elif alert["severity"] == "success":
                st.success(alert["message"])
            elif alert["severity"] == "error":
                st.error(alert["message"])
            else:
                st.info(alert["message"])

            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("🔎 Open Job", key=f"alert_open_{idx}", use_container_width=True):
                    if alert.get("job_id") in jobs:
                        st.session_state.selected_job_id = alert.get("job_id")
                        st.rerun()
            with a2:
                if st.button("🎯 Apply Preset", key=f"alert_preset_{idx}", use_container_width=True):
                    target_job = alert.get("job_id")
                    if target_job and target_job in jobs:
                        st.session_state.selected_job_id = target_job
                        st.session_state[f"saved_preset_{target_job}"] = alert.get("preset", "All")
                    st.rerun()
            with a3:
                if st.button("✅ Resolve", key=f"alert_resolve_{idx}", use_container_width=True):
                    resolved_now = set(st.session_state.get("resolved_alert_ids", []))
                    resolved_now.add(alert["id"])
                    st.session_state.resolved_alert_ids = list(resolved_now)
                    add_activity(current_host_id, "alert_resolved", alert["message"])
                    st.rerun()

    st.markdown("<h4 style='color:#A8D5BA;'>Team & Role Permissions</h4>", unsafe_allow_html=True)
    roles = load_host_roles()
    if is_admin:
        role_hosts = list(roles.keys()) if roles else [current_host_id]
        selected_host_for_role = st.selectbox("Select host", role_hosts, key="role_host_selector")
        role_val = st.selectbox("Assign role", ["admin", "recruiter", "viewer"], index=["admin", "recruiter", "viewer"].index(roles.get(selected_host_for_role, "viewer")), key="role_value_selector")
        if st.button("💾 Update Role", key="btn_update_role", use_container_width=True):
            set_host_role(selected_host_for_role, role_val)
            add_activity(current_host_id, "role_updated", f"{selected_host_for_role} -> {role_val}")
            st.success("✅ Role updated")
            st.rerun()
    else:
        st.info("Only admin can change team roles")

    # -------- QUICK ACTION BUTTONS --------
    st.markdown("<h4 style='color:#A8D5BA;'>Quick Actions</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Create New Job", use_container_width=True, key="quick_create_job", disabled=not can_manage_jobs):
            st.session_state.host_page = "create_job"
            st.rerun()
    
    with col2:
        if st.button("👥 View User Profiles", use_container_width=True, key="quick_view_users"):
            st.session_state.host_page = "view_users"
            st.rerun()
    
    with col3:
        if st.button("🤖 Analyse All Resumes", use_container_width=True, key="quick_analyse_all"):
            st.session_state.host_page = "analyse_all"
            st.rerun()
    
    with col4:
        if st.button("🗑️ Delete Job", use_container_width=True, key="quick_delete_job", disabled=not is_admin):
            st.session_state.host_page = "delete_job"
            st.rerun()
    
    # -------- MESSAGES PAGE --------
    if st.session_state.host_page == "messages":
        host_chat_interface()
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.host_page = "main"
            st.session_state.host_chat_page = "inbox"
            st.session_state.current_host_conversation = None
            st.rerun()
        return
    
    # Add messages button
    col5 = st.columns(4)[-1]
    with col5:
        if st.button("💬 Messages", use_container_width=True, key="quick_messages"):
            st.session_state.host_page = "messages"
            st.rerun()

    st.markdown("---")

    if not jobs:
        st.warning("📋 No jobs found. Please create jobs first.")
        return

    # Initialize selected job if not exists
    if "selected_job_id" not in st.session_state:
        st.session_state.selected_job_id = None
    
    # -------- JOB SPECIFIC PANEL --------
    if st.session_state.selected_job_id and st.session_state.selected_job_id in jobs:
        job_id = st.session_state.selected_job_id
        job_info = jobs[job_id]
        
        # Header with back button
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("⬅️ Back to Jobs", use_container_width=True):
                st.session_state.selected_job_id = None
                st.rerun()
        with col_title:
            st.markdown(f"<h2 style='color:#A8D5BA; margin:0;'>📋 {job_info['title']}</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Job details summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Job ID", job_id)
        with col2:
            st.metric("📍 Location", job_info.get('location', 'N/A'))
        with col3:
            applications = get_applications_by_job(job_id)
            st.metric("👥 Total Applications", len(applications))
        
        st.markdown("---")
        
        # Job description
        st.markdown("<h4 style='color:#A8D5BA;'>📝 Job Description</h4>", unsafe_allow_html=True)
        st.write(job_info.get('description', 'N/A'))
        
        if job_info.get('keywords'):
            st.markdown("<h4 style='color:#A8D5BA;'>🔑 Required Skills</h4>", unsafe_allow_html=True)
            skill_tags = " ".join([f"🏷️ `{k}`" for k in job_info.get('keywords', [])])
            st.markdown(skill_tags)
        
        st.markdown("---")
        
        # Candidates section
        st.markdown("<h3 style='color:#A8D5BA;'>👥 Applicants</h3>", unsafe_allow_html=True)

        if not applications:
            st.info("📭 No candidates have applied for this job yet.")
        else:
            users_all = load_users()
            stage_map = {
                "Applied": "Applied",
                "Under Review": "Applied",
                "Shortlisted": "Shortlisted",
                "Interview": "Interview",
                "Offer": "Offer",
                "Hired": "Hired",
                "Rejected": "Rejected"
            }
            pipeline_stages = ["Applied", "Shortlisted", "Interview", "Offer", "Hired"]

            st.markdown("<h4 style='color:#A8D5BA;'>Hiring Pipeline Board (Drag/Drop Style)</h4>", unsafe_allow_html=True)
            pcols = st.columns(5)
            for idx, stage in enumerate(pipeline_stages):
                stage_candidates = []
                for uid, info in applications.items():
                    current_stage = stage_map.get(info.get("status", "Applied"), "Applied")
                    if current_stage == stage:
                        stage_candidates.append(uid)
                with pcols[idx]:
                    st.markdown(f"**{stage}**")
                    st.metric("Count", len(stage_candidates))
                    if stage_candidates:
                        for uid in stage_candidates[:8]:
                            score = applications[uid].get("score")
                            st.caption(f"• {uid} ({score if score is not None else 'NA'})")

            move_col1, move_col2, move_col3, move_col4 = st.columns([1.5, 2.2, 1.5, 1.2])
            with move_col1:
                from_stage = st.selectbox("From", pipeline_stages, key=f"pipe_from_{job_id}")
            with move_col2:
                movable_users = [
                    uid for uid, info in applications.items()
                    if stage_map.get(info.get("status", "Applied"), "Applied") == from_stage
                ]
                move_users = st.multiselect("Candidates", movable_users, key=f"pipe_users_{job_id}")
            with move_col3:
                to_stage = st.selectbox("To", pipeline_stages, key=f"pipe_to_{job_id}")
            with move_col4:
                if st.button("Move", key=f"pipe_move_{job_id}", use_container_width=True, disabled=not can_manage_jobs):
                    moved = 0
                    for uid in move_users:
                        if update_application_status_with_log(job_id, uid, to_stage, current_host_id):
                            moved += 1
                    if moved:
                        st.success(f"✅ Moved {moved} candidate(s) to {to_stage}")
                        st.rerun()

            st.markdown("<h4 style='color:#A8D5BA;'>Saved Views & Presets</h4>", unsafe_allow_html=True)
            preset = st.selectbox(
                "Preset",
                ["All", "Urgent roles", "High-score candidates", "Interview today"],
                key=f"saved_preset_{job_id}"
            )

            st.markdown("<h4 style='color:#A8D5BA;'>Actionable Candidate Table</h4>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                status_filter = st.selectbox("Status", ["All", "Applied", "Under Review", "Shortlisted", "Interview", "Offer", "Hired", "Rejected"], key=f"status_filter_{job_id}")
            with c2:
                score_filter = st.selectbox("Score", ["All", "≥80", "60-79", "<60"], key=f"score_filter_{job_id}")
            with c3:
                location_filter = st.text_input("Location contains", key=f"location_filter_{job_id}")
            with c4:
                skills_filter = st.text_input("Skills contains", key=f"skills_filter_{job_id}")

            rows = []
            for uid, info in applications.items():
                user_profile = users_all.get(uid, {}).get("profile", {})
                score = info.get("score")
                status_val = info.get("status", "Applied")
                applied_text = info.get("applied_at", "N/A")
                applied_dt = parse_dt(applied_text)
                rows.append({
                    "candidate_key": f"{job_id}::{uid}",
                    "user_id": uid,
                    "status": status_val,
                    "score": score if score is not None else -1,
                    "display_score": "Pending" if score is None else f"{score}",
                    "location": (user_profile.get("city") or job_info.get("location") or "N/A"),
                    "skills": ", ".join(user_profile.get("skills", [])) if user_profile.get("skills") else "N/A",
                    "applied_at": applied_text,
                    "applied_dt": applied_dt
                })

            filtered_rows = rows[:]
            if preset == "High-score candidates":
                filtered_rows = [r for r in filtered_rows if r["score"] >= 80]
            elif preset == "Interview today":
                today_text = datetime.now().strftime("%Y-%m-%d")
                filtered_rows = [r for r in filtered_rows if r["status"] == "Interview" and str(r["applied_at"]).startswith(today_text)]
            elif preset == "Urgent roles":
                cutoff = datetime.now() - timedelta(days=7)
                filtered_rows = [r for r in filtered_rows if r["status"] in ["Applied", "Under Review"] and r["applied_dt"] and r["applied_dt"] < cutoff]

            if status_filter != "All":
                filtered_rows = [r for r in filtered_rows if r["status"] == status_filter]
            if score_filter == "≥80":
                filtered_rows = [r for r in filtered_rows if r["score"] >= 80]
            elif score_filter == "60-79":
                filtered_rows = [r for r in filtered_rows if 60 <= r["score"] < 80]
            elif score_filter == "<60":
                filtered_rows = [r for r in filtered_rows if r["score"] < 60]
            if location_filter.strip():
                filtered_rows = [r for r in filtered_rows if location_filter.lower() in str(r["location"]).lower()]
            if skills_filter.strip():
                filtered_rows = [r for r in filtered_rows if skills_filter.lower() in str(r["skills"]).lower()]

            filtered_rows = sorted(filtered_rows, key=lambda r: (r["score"], r["applied_dt"] or datetime.min), reverse=True)
            if filtered_rows:
                table_data = [{
                    "Candidate": r["user_id"],
                    "Status": r["status"],
                    "Score": r["display_score"],
                    "Location": r["location"],
                    "Skills": r["skills"],
                    "Applied": str(r["applied_at"])[:10]
                } for r in filtered_rows]
                st.dataframe(table_data, use_container_width=True)
            else:
                st.info("No candidates match current filters")

            selected_keys = st.multiselect(
                "Select candidates for bulk action",
                options=[r["candidate_key"] for r in filtered_rows],
                format_func=lambda x: x.split("::")[1],
                key=f"bulk_select_{job_id}"
            )

            b1, b2, b3, b4 = st.columns(4)
            with b1:
                if st.button("Bulk Shortlist", use_container_width=True, key=f"bulk_shortlist_{job_id}", disabled=(not selected_keys or not can_manage_jobs)):
                    for key in selected_keys:
                        _, uid = key.split("::")
                        update_application_status_with_log(job_id, uid, "Shortlisted", current_host_id)
                    st.success("✅ Bulk shortlist completed")
                    st.rerun()
            with b2:
                if st.button("Bulk Reject", use_container_width=True, key=f"bulk_reject_{job_id}", disabled=(not selected_keys or not can_manage_jobs)):
                    for key in selected_keys:
                        _, uid = key.split("::")
                        update_application_status_with_log(job_id, uid, "Rejected", current_host_id)
                    st.success("✅ Bulk reject completed")
                    st.rerun()
            with b3:
                if st.button("Bulk Message", use_container_width=True, key=f"bulk_msg_{job_id}", disabled=(not selected_keys)):
                    st.info(f"💬 Ready to message {len(selected_keys)} candidates from Messages panel")
            with b4:
                export_buffer = StringIO()
                writer = csv.DictWriter(export_buffer, fieldnames=["Candidate", "Status", "Score", "Location", "Skills", "Applied"])
                writer.writeheader()
                for row in [{
                    "Candidate": r["user_id"],
                    "Status": r["status"],
                    "Score": r["display_score"],
                    "Location": r["location"],
                    "Skills": r["skills"],
                    "Applied": str(r["applied_at"])[:10]
                } for r in filtered_rows]:
                    writer.writerow(row)
                st.download_button(
                    "Export CSV",
                    data=export_buffer.getvalue(),
                    file_name=f"candidates_{job_id}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"export_csv_{job_id}"
                )

            st.markdown("<h4 style='color:#A8D5BA;'>Job Health Analytics</h4>", unsafe_allow_html=True)
            funnel_counts = {
                "Applied": 0,
                "Shortlisted": 0,
                "Interview": 0,
                "Offer": 0,
                "Hired": 0,
                "Rejected": 0
            }
            score_quality = {"High (80+)": 0, "Medium (60-79)": 0, "Low (<60)": 0, "Pending": 0}
            weekly = {}
            monthly = {}
            for _, info in applications.items():
                stg = info.get("status", "Applied")
                if stg in funnel_counts:
                    funnel_counts[stg] += 1
                elif stg == "Under Review":
                    funnel_counts["Applied"] += 1

                score = info.get("score")
                if score is None:
                    score_quality["Pending"] += 1
                elif score >= 80:
                    score_quality["High (80+)"] += 1
                elif score >= 60:
                    score_quality["Medium (60-79)"] += 1
                else:
                    score_quality["Low (<60)"] += 1

                applied_dt = parse_dt(info.get("applied_at"))
                if applied_dt:
                    week_key = f"{applied_dt.isocalendar().year}-W{applied_dt.isocalendar().week:02d}"
                    month_key = applied_dt.strftime("%Y-%m")
                    weekly[week_key] = weekly.get(week_key, 0) + 1
                    monthly[month_key] = monthly.get(month_key, 0) + 1

            a1, a2 = st.columns(2)
            with a1:
                st.caption("Per-job conversion funnel")
                st.bar_chart(funnel_counts)
                drop_off = max(funnel_counts.items(), key=lambda x: x[1])[0] if sum(funnel_counts.values()) else "N/A"
                st.info(f"Biggest stage volume / potential drop-off: {drop_off}")
            with a2:
                st.caption("Source quality (score distribution)")
                st.bar_chart(score_quality)

            t1, t2 = st.columns(2)
            with t1:
                st.caption("Weekly trend")
                st.line_chart(dict(sorted(weekly.items())) if weekly else {"No data": 0})
            with t2:
                st.caption("Monthly trend")
                st.line_chart(dict(sorted(monthly.items())) if monthly else {"No data": 0})

            st.markdown("<h4 style='color:#A8D5BA;'>Professional Activity Log</h4>", unsafe_allow_html=True)
            logs = [x for x in load_activity_log() if job_id in x.get("details", "")]
            logs = sorted(logs, key=lambda x: x.get("at", ""), reverse=True)
            if logs:
                st.dataframe([
                    {
                        "Time": l.get("at", "")[:19].replace("T", " "),
                        "Actor": l.get("actor", "N/A"),
                        "Action": l.get("action", "N/A"),
                        "Details": l.get("details", "")
                    } for l in logs[:30]
                ], use_container_width=True)
            else:
                st.info("No activity logs for this job yet")
    
    else:
        # -------- JOBS LIST PAGE --------
        st.markdown("<h3 style='color:#A8D5BA;'>📋 Your Job Postings</h3>", unsafe_allow_html=True)
        
        if not jobs:
            st.info("📭 No jobs created yet. Click 'Create New Job' to get started!")
        else:
            # Display jobs as professional cards
            for job_id, job_info in jobs.items():
                applications = get_applications_by_job(job_id)
                shortlisted = sum(1 for app in applications.values() if app.get('status') == 'Shortlisted')
                
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.06); border: 1px solid rgba(168, 213, 186, 0.3); border-radius: 12px; padding: 20px; margin: 16px 0; cursor: pointer;'>
                    <div style='display: flex; justify-content: space-between; align-items: start;'>
                        <div style='flex: 1;'>
                            <h4 style='color: #A8D5BA; margin: 0 0 8px 0;'>{job_info['title']}</h4>
                            <p style='color: #999; margin: 0 0 12px 0; font-size: 14px;'>📍 {job_info.get('location', 'N/A')}</p>
                            <p style='color: #d0d0d0; margin: 0; font-size: 13px; line-height: 1.4;'>{job_info.get('description', 'N/A')[:150]}...</p>
                        </div>
                        <div style='text-align: right; margin-left: 20px;'>
                            <div style='background: rgba(168, 213, 186, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
                                <div style='color: #A8D5BA; font-weight: bold; font-size: 20px;'>{len(applications)}</div>
                                <div style='color: #999; font-size: 12px;'>Applications</div>
                            </div>
                            <div style='font-size: 12px; color: #7ED321;'>✓ {shortlisted} Shortlisted</div>
                        </div>
                    </div>
                    <div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(168, 213, 186, 0.2);'>
                        <small style='color: #999;'>Job ID: {job_id}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # View details button
                if st.button(f"👁️ View & Manage Candidates", key=f"view_job_{job_id}", use_container_width=True):
                    st.session_state.selected_job_id = job_id
                    st.rerun()
                
                st.markdown("")
    
    # Back navigation for main jobs list
    st.markdown("---")
    col_nav = st.columns([1, 2, 1])
    with col_nav[0]:
        if st.button("⬅️ Back to Roles", use_container_width=True, key="btn_back_roles"):
            st.session_state.page = "role"
            st.session_state.host_page = "main"
            st.rerun()



