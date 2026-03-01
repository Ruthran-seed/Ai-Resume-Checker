import streamlit as st
import json
import os
import time
from datetime import datetime

from host_applications import get_applications_by_job
from resume_parser import extract_text_from_pdf
from ai_matching import calculate_match_score, get_match_details
from score_updater import update_score
from status_updater import update_status
from host_chat import host_chat_interface
from chat_manager import get_conversation_id
from auth import create_user

# ============ FILE PATHS ============
JOB_FILE = "jobs.json"
USER_FILE = "users.json"
APP_FILE = "applications.json"

# ============ HELPERS ============
def load_jobs():
    if os.path.exists(JOB_FILE):
        try:
            with open(JOB_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
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
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: {USER_FILE} is corrupted, resetting to empty dict")
            return {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

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

def save_applications_data(applications):
    with open(APP_FILE, "w") as f:
        json.dump(applications, f, indent=2)

def cleanup_user_related_data(user_id, users):
    applications = load_applications_data()
    removed_applications = 0

    for job_id in list(applications.keys()):
        if user_id in applications[job_id]:
            del applications[job_id][user_id]
            removed_applications += 1

    save_applications_data(applications)

    removed_files = []
    profile = users.get(user_id, {}).get("profile", {})
    avatar_path = profile.get("avatar") if profile else None
    if avatar_path and os.path.exists(avatar_path):
        try:
            os.remove(avatar_path)
            removed_files.append(avatar_path)
        except Exception:
            pass

    for ext in [".pdf", ".doc", ".docx"]:
        resume_path = os.path.join("resumes", f"{user_id}{ext}")
        if os.path.exists(resume_path):
            try:
                os.remove(resume_path)
                removed_files.append(resume_path)
            except Exception:
                pass

    return removed_applications, removed_files

def generate_job_id():
    import random
    return "JOB" + str(random.randint(1000, 9999))

def create_job_entry(title, location, description, keywords, posted_by=None):
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
        "posted_by": posted_by or "Unknown",
        "created_at": str(datetime.now())
    }
    save_jobs(jobs)
    return job_id



# ============ MODERN CSS STYLING ============
MODERN_CSS = """
<style>
/* Main container styling */
.host-panel-container {
    background: linear-gradient(135deg, rgba(10, 14, 20, 1), rgba(20, 25, 35, 1));
    border-radius: 16px;
    padding: 24px;
    margin: 0 -16px;
}

/* Header section */
.panel-header {
    text-align: center;
    margin-bottom: 32px;
    padding: 28px;
    background: linear-gradient(135deg, rgba(168, 213, 186, 0.1), rgba(168, 213, 186, 0.05));
    border-radius: 16px;
    border: 1px solid rgba(168, 213, 186, 0.2);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.panel-title {
    color: #A8D5BA;
    font-size: 28px;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.panel-subtitle {
    color: #b0b0b0;
    font-size: 14px;
    margin: 8px 0 0 0;
    font-weight: 400;
}

/* Quick action buttons section */
.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}

/* Card styling */
.job-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(168, 213, 186, 0.25);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.job-card:hover {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-color: rgba(168, 213, 186, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(168, 213, 186, 0.15);
}

/* Candidate card */
.candidate-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border-left: 4px solid #A8D5BA;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    backdrop-filter: blur(10px);
    transition: all 0.2s ease;
}

.candidate-card:hover {
    background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%);
    box-shadow: 0 4px 12px rgba(168, 213, 186, 0.1);
}

/* Metrics row */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin: 16px 0;
}

.metric-card {
    background: linear-gradient(135deg, rgba(168, 213, 186, 0.1), rgba(168, 213, 186, 0.05));
    border: 1px solid rgba(168, 213, 186, 0.2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s ease;
}

.metric-card:hover {
    background: linear-gradient(135deg, rgba(168, 213, 186, 0.15), rgba(168, 213, 186, 0.08));
    border-color: rgba(168, 213, 186, 0.4);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #A8D5BA;
    margin: 8px 0;
}

.metric-label {
    font-size: 12px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-applied {
    background: rgba(74, 144, 226, 0.2);
    color: #4A90E2;
    border: 1px solid rgba(74, 144, 226, 0.3);
}

.status-review {
    background: rgba(245, 166, 35, 0.2);
    color: #F5A623;
    border: 1px solid rgba(245, 166, 35, 0.3);
}

.status-shortlisted {
    background: rgba(126, 211, 33, 0.2);
    color: #7ED321;
    border: 1px solid rgba(126, 211, 33, 0.3);
}

.status-rejected {
    background: rgba(208, 2, 27, 0.2);
    color: #D0021B;
    border: 1px solid rgba(208, 2, 27, 0.3);
}

/* Score badge */
.score-excellent {
    color: #7ED321;
    font-weight: 700;
}

.score-good {
    color: #F5A623;
    font-weight: 700;
}

.score-poor {
    color: #D0021B;
    font-weight: 700;
}

/* Section divider */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168, 213, 186, 0.3), transparent);
    margin: 24px 0;
    border: none;
}

/* Filter box */
.filter-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(168, 213, 186, 0.15);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 20px;
}

/* Header gradient text */
.gradient-text {
    background: linear-gradient(135deg, #A8D5BA, #7ED321);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Empty state styling */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999;
}

.empty-state-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

/* Smooth transitions */
[data-testid="stButton"] button {
    transition: all 0.2s ease !important;
}

[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
}
</style>
"""

# ============ MAIN DASHBOARD FUNCTION ============
def host_dashboard():
    # Apply modern CSS
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    
    # Initialize session states
    if "host_page" not in st.session_state:
        st.session_state.host_page = "main"
    if "selected_job_id" not in st.session_state:
        st.session_state.selected_job_id = None
    
    # ========== HEADER SECTION ==========
    st.markdown("""
    <div class="panel-header">
        <h1 class="panel-title">👔 Host Control Panel</h1>
        <p class="panel-subtitle">Manage jobs, review candidates & make hiring decisions with AI-powered analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== PAGE ROUTING ==========
    
    # CREATE JOB PAGE
    if st.session_state.host_page == "create_job":
        create_job_page()
        return
    
    # VIEW USERS PAGE
    elif st.session_state.host_page == "view_users":
        view_users_page()
        return
    
    # ANALYSE ALL PAGE
    elif st.session_state.host_page == "analyse_all":
        analyse_all_page()
        return
    
    # DELETE JOB PAGE
    elif st.session_state.host_page == "delete_job":
        delete_job_page()
        return
    
    # CREATE USER PAGE
    elif st.session_state.host_page == "create_user":
        create_user_page()
        return
    
    # DELETE USER PAGE
    elif st.session_state.host_page == "delete_user":
        delete_user_page()
        return
    
    # MESSAGES PAGE
    elif st.session_state.host_page == "messages":
        host_chat_interface()
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.host_page = "main"
            st.session_state.host_chat_page = "inbox"
            st.session_state.current_host_conversation = None
            st.rerun()
        return
    
    # JOB DETAIL PAGE
    elif st.session_state.host_page == "job_detail":
        job_detail_page()
        return

    # JOB POSTINGS PAGE
    elif st.session_state.host_page == "job_postings":
        job_postings_page()
        return
    
    # MAIN DASHBOARD
    else:
        main_dashboard_page()

# ============ PAGE FUNCTIONS ============

def create_job_page():
    """Create new job posting page"""
    # Professional header
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.15), rgba(168, 213, 186, 0.05)); 
                border: 1px solid rgba(168, 213, 186, 0.3); border-radius: 16px; padding: 32px; margin-bottom: 28px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);'>
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 12px;'>
            <div style='font-size: 32px;'>➕</div>
            <div>
                <h1 style='color:#A8D5BA; margin:0; font-size:28px; font-weight:700;'>Create New Job Posting</h1>
            </div>
        </div>
        <p style='color:#b0b0b0; margin:8px 0 0 0; font-size:14px;'>Post a new position and attract qualified candidates to your team</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("create_job_form"):
        # Basic Information Section
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>📋 Basic Information</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            title = st.text_input("Job Title *", placeholder="e.g., Senior Python Developer", key="job_title")
        
        with col2:
            location = st.text_input("Location *", placeholder="e.g., New York, NY", key="job_location")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Job Details Section
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>📝 Job Details</h3>", unsafe_allow_html=True)
        
        description = st.text_area("Job Description *", placeholder="Enter detailed job description, responsibilities, and requirements...", height=180, key="job_desc")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Requirements Section
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>🏷️ Required Skills</h3>", unsafe_allow_html=True)
        
        keywords = st.text_input("Skills (comma-separated)", placeholder="e.g., Python, Django, REST API, Docker, Git", key="job_skills")
        st.caption("💡 Tip: Separate multiple skills with commas")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action Buttons
        st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            submit = st.form_submit_button("✅ Post Job", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if submit:
            if not title or not location or not description:
                st.error("❌ Please fill all required fields marked with *")
            else:
                with st.spinner("📝 Creating job posting..."):
                    host_id = st.session_state.get('current_host_id') or st.session_state.get('host_id')
                    job_id = create_job_entry(
                        title, 
                        location, 
                        description, 
                        keywords,
                        posted_by=host_id
                    )
                    time.sleep(0.5)
                st.success(f"✅ Job posted successfully! 🎉")
                st.info(f"**Job ID:** `{job_id}` | **Title:** {title} | **Location:** {location}")
                st.balloons()
                time.sleep(2)
                st.session_state.host_page = "main"
                st.rerun()
        
        if cancel:
            st.session_state.host_page = "main"
            st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def view_users_page():
    """View all user profiles"""
    # Professional header
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.15), rgba(168, 213, 186, 0.05)); 
                border: 1px solid rgba(168, 213, 186, 0.3); border-radius: 16px; padding: 32px; margin-bottom: 28px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);'>
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 12px;'>
            <div style='font-size: 32px;'>👥</div>
            <div>
                <h1 style='color:#A8D5BA; margin:0; font-size:28px; font-weight:700;'>User Profiles</h1>
            </div>
        </div>
        <p style='color:#b0b0b0; margin:8px 0 0 0; font-size:14px;'>Manage and view all registered users in the system</p>
    </div>
    """, unsafe_allow_html=True)
    
    users = load_users()
    
    if not users:
        st.markdown("""
        <div style='background: rgba(168, 213, 186, 0.08); border: 1px dashed rgba(168, 213, 186, 0.3); 
                    border-radius: 12px; padding: 60px 20px; text-align: center; margin: 40px 0;'>
            <div style='font-size: 48px; margin-bottom: 16px;'>👤</div>
            <p style='color:#b0b0b0; font-size: 16px; margin: 0;'>No users found in the system</p>
            <p style='color:#999; font-size: 13px; margin-top: 8px;'>Users will appear here once they register or are created</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Statistics with enhanced styling
        col1, col2, col3 = st.columns(3, gap="medium")
        
        total_users = len(users)
        users_with_profile = sum(1 for u in users.values() if u.get('profile', {}).get('name'))
        unique_emails = len(set(u.get('email') for u in users.values()))
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.1), rgba(168, 213, 186, 0.05));
                        border: 1px solid rgba(168, 213, 186, 0.2); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 24px; color: #A8D5BA; font-weight: 700;'>{total_users}</div>
                <div style='color: #999; font-size: 12px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px;'>Total Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(126, 211, 33, 0.1), rgba(126, 211, 33, 0.05));
                        border: 1px solid rgba(126, 211, 33, 0.2); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 24px; color: #7ED321; font-weight: 700;'>{users_with_profile}</div>
                <div style='color: #999; font-size: 12px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px;'>Complete Profiles</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(245, 166, 35, 0.1), rgba(245, 166, 35, 0.05));
                        border: 1px solid rgba(245, 166, 35, 0.2); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 24px; color: #F5A623; font-weight: 700;'>{unique_emails}</div>
                <div style='color: #999; font-size: 12px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px;'>Registered Emails</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
        
        # Search and filter
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        search_term = st.text_input("🔍 Search users", placeholder="Search by name or email...", key="user_search")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Filter users
        filtered_users = users
        if search_term:
            filtered_users = {
                k: v for k, v in users.items()
                if search_term.lower() in v.get('email', '').lower() or
                   search_term.lower() in v.get('profile', {}).get('name', '').lower()
            }
        
        if not filtered_users:
            st.info("❌ No users match your search criteria")
        else:
            st.markdown(f"<p style='color: #999; font-size: 12px; margin-bottom: 16px;'>Found {len(filtered_users)} user(s)</p>", unsafe_allow_html=True)
            
            for user_id, user_data in filtered_users.items():
                profile = user_data.get('profile', {})
                profile_status = '✅ Complete' if profile.get('name') else '⏳ Incomplete'
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
                            border: 1px solid rgba(168, 213, 186, 0.2); border-radius: 12px; padding: 20px; margin: 12px 0;
                            backdrop-filter: blur(10px); transition: all 0.2s ease;'>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;'>
                        <div style='flex: 1;'>
                            <h4 style='color: #A8D5BA; margin: 0 0 4px 0; font-size: 16px;'>{profile.get('name', 'No Name Set')}</h4>
                            <p style='color: #999; margin: 0 0 6px 0; font-size: 13px;'>📧 {user_data.get('email', 'N/A')}</p>
                            <p style='color: #999; margin: 0; font-size: 12px;'>👤 ID: <code>{user_id}</code></p>
                        </div>
                        <div style='text-align: right;'>
                            <span style='background: rgba(126, 211, 33, 0.2); color: #7ED321; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;'>{profile_status}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"📋 View Full Profile → {profile.get('name', user_id)}", expanded=False):
                    col1, col2 = st.columns(2, gap="medium")
                    
                    with col1:
                        st.markdown("<h4 style='color: #A8D5BA;'>👤 Personal Information</h4>", unsafe_allow_html=True)
                        avatar_path = profile.get("avatar")
                        if avatar_path and os.path.exists(avatar_path):
                            st.image(avatar_path, width=150, caption="Profile Picture", use_column_width=False)
                        else:
                            st.markdown("<div style='background: rgba(168, 213, 186, 0.1); padding: 40px; text-align: center; border-radius: 8px;'><p style='color: #999; margin: 0;'>No Picture</p></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<p><strong>📱 Phone:</strong><br><code>{profile.get('phone', 'N/A')}</code></p>", unsafe_allow_html=True)
                        st.markdown(f"<p><strong>📍 City:</strong><br>{profile.get('city', 'N/A')}</p>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h4 style='color: #A8D5BA;'>📚 Professional Information</h4>", unsafe_allow_html=True)
                        
                        st.markdown(f"<p><strong>🎓 Qualification:</strong><br>{profile.get('qualification', 'N/A')}</p>", unsafe_allow_html=True)
                        
                        skills = profile.get('skills', [])
                        skills_html = '<br>'.join([f"<span style='background: rgba(168, 213, 186, 0.2); color: #A8D5BA; padding: 2px 6px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 12px;'>{skill}</span>" for skill in skills]) if skills else 'N/A'
                        st.markdown(f"<p><strong>🏷️ Skills:</strong><br>{skills_html}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def analyse_all_page():
    """Analyze all resumes page"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.1), rgba(168, 213, 186, 0.05)); 
                border-left: 4px solid #A8D5BA; border-radius: 8px; padding: 16px; margin-bottom: 24px;'>
        <h2 style='color:#A8D5BA; margin:0;'>🤖 AI Resume Analysis</h2>
        <p style='color:#b0b0b0; margin:8px 0 0 0;'>Analyze all candidate resumes for a specific job</p>
    </div>
    """, unsafe_allow_html=True)
    
    jobs = load_jobs()
    
    if not jobs:
        st.warning("📋 No jobs found. Create a job first.")
    else:
        job_id = st.selectbox(
            "Select a job to analyze resumes for",
            options=list(jobs.keys()),
            format_func=lambda x: f"{x} — {jobs[x]['title']}"
        )
        
        if st.button("🚀 Analyze All Resumes", use_container_width=True):
            applications = get_applications_by_job(job_id)
            
            if not applications:
                st.warning("📭 No applications for this job")
            else:
                st.info(f"🔄 Analyzing {len(applications)} resumes with AI...")
                
                job_desc = jobs[job_id].get("description", "")
                scores_updated = 0
                errors = []
                
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for idx, (user_id, info) in enumerate(applications.items()):
                    resume_path = info.get("resume")
                    
                    progress_text.text(f"Processing {idx + 1}/{len(applications)}: {user_id}")
                    
                    if resume_path and os.path.exists(resume_path):
                        try:
                            resume_text = extract_text_from_pdf(resume_path)
                            score = calculate_match_score(resume_text, job_desc)
                            update_score(job_id, user_id, score)
                            scores_updated += 1
                        except Exception as e:
                            errors.append(f"{user_id}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(applications))
                
                progress_text.empty()
                st.success(f"✅ Analysis complete! Updated {scores_updated}/{len(applications)} resumes")
                
                if errors:
                    with st.expander("⚠️ Errors during analysis"):
                        for error in errors:
                            st.write(f"- {error}")
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def delete_job_page():
    """Delete job page"""
    # Professional header
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(208, 2, 27, 0.15), rgba(208, 2, 27, 0.05)); 
                border: 1px solid rgba(208, 2, 27, 0.3); border-radius: 16px; padding: 32px; margin-bottom: 28px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);'>
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 12px;'>
            <div style='font-size: 32px;'>🗑️</div>
            <div>
                <h1 style='color:#D0021B; margin:0; font-size:28px; font-weight:700;'>Delete Job Posting</h1>
            </div>
        </div>
        <p style='color:#b0b0b0; margin:8px 0 0 0; font-size:14px;'>Permanently remove a job from the system</p>
    </div>
    """, unsafe_allow_html=True)
    
    jobs = load_jobs()
    
    if not jobs:
        st.markdown("""
        <div style='background: rgba(208, 2, 27, 0.08); border: 1px dashed rgba(208, 2, 27, 0.3); 
                    border-radius: 12px; padding: 60px 20px; text-align: center; margin: 40px 0;'>
            <div style='font-size: 48px; margin-bottom: 16px;'>📋</div>
            <p style='color:#b0b0b0; font-size: 16px; margin: 0;'>No job postings found</p>
            <p style='color:#999; font-size: 13px; margin-top: 8px;'>Create a job posting first before attempting to delete</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='background: rgba(208, 2, 27, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#D0021B; margin-top:0;'>📋 Select Job to Delete</h3>", unsafe_allow_html=True)
        
        job_id = st.selectbox(
            "Choose a job posting",
            options=list(jobs.keys()),
            format_func=lambda x: f"{x} — {jobs[x]['title']} ({jobs[x].get('location', 'N/A')})",
            key="delete_job_selector"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        job_info = jobs[job_id]
        applications = get_applications_by_job(job_id)
        
        # Job details preview
        st.markdown("<div style='background: rgba(168, 213, 186, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>👁️ Job Details Preview</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            st.markdown(f"<p><strong>Title</strong><br><code>{job_info.get('title')}</code></p>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p><strong>Location</strong><br>{job_info.get('location', 'N/A')}</p>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<p><strong>Applications</strong><br><span style='font-size: 20px; color: #A8D5BA; font-weight: 700;'>{len(applications)}</span></p>", unsafe_allow_html=True)
        
        st.markdown("<p><strong>Description</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #d0d0d0; line-height: 1.6;'>{job_info.get('description', 'N/A')}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Warning
        st.warning(f"⚠️ **This action is permanent!** You are about to delete **{job_info.get('title')}**. The {len(applications)} associated applications will remain in the system but will be orphaned.", icon="⚠️")
        
        # Action buttons
        st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🗑️ Confirm Delete", use_container_width=True, key="confirm_delete"):
                with st.spinner("Deleting job..."):
                    del jobs[job_id]
                    save_jobs(jobs)
                    time.sleep(0.5)
                st.success(f"✅ Job {job_id} has been deleted successfully")
                st.balloons()
                time.sleep(2)
                st.session_state.host_page = "main"
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_delete"):
                st.session_state.host_page = "main"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def create_user_page():
    """Create new user account"""
    # Professional header
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.15), rgba(168, 213, 186, 0.05)); 
                border: 1px solid rgba(168, 213, 186, 0.3); border-radius: 16px; padding: 32px; margin-bottom: 28px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);'>
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 12px;'>
            <div style='font-size: 32px;'>👤➕</div>
            <div>
                <h1 style='color:#A8D5BA; margin:0; font-size:28px; font-weight:700;'>Create New User Account</h1>
            </div>
        </div>
        <p style='color:#b0b0b0; margin:8px 0 0 0; font-size:14px;'>Add a new user to the system with login credentials</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("create_user_form"):
        # Account Information Section
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>📧 Account Information</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            email = st.text_input("Email Address *", placeholder="e.g., john.doe@example.com", key="user_email")
        
        with col2:
            user_id = st.text_input("User ID *", placeholder="e.g., john_doe_123", key="user_id")
            st.caption("💡 Alphanumeric & underscores only, 4-15 chars")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Security Section
        st.markdown("<div style='background: rgba(168, 213, 186, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#A8D5BA; margin-top:0;'>🔐 Security</h3>", unsafe_allow_html=True)
        
        password = st.text_input("Password *", type="password", placeholder="Min 6 chars, letters + numbers", key="user_pwd")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password", key="user_pwd_confirm")
        st.caption("💡 Password requirements: Minimum 6 characters with both letters and numbers")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action Buttons
        st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            submit = st.form_submit_button("✅ Create User", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if submit:
            # Validation
            if not email or not user_id or not password or not confirm_password:
                st.error("❌ Please fill all fields marked with *")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif "@" not in email:
                st.error("❌ Please enter a valid email address")
            else:
                with st.spinner("👤 Creating user account..."):
                    result_id, message = create_user(email, user_id, password)
                    time.sleep(0.5)
                
                if result_id:
                    st.success(f"✅ User account created successfully! 🎉")
                    st.markdown(f"""
                    <div style='background: rgba(126, 211, 33, 0.1); border: 1px solid rgba(126, 211, 33, 0.3); 
                                border-radius: 12px; padding: 16px; margin: 16px 0;'>
                        <h4 style='color: #7ED321; margin-top: 0;'>👤 Account Details</h4>
                        <p style='margin: 8px 0;'><strong>User ID:</strong> <code>{result_id}</code></p>
                        <p style='margin: 8px 0;'><strong>Email:</strong> <code>{email}</code></p>
                        <p style='margin: 8px 0;'><strong>Password:</strong> <code>{password}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.warning("⚠️ Make sure to share these credentials with the user securely. This is their only email!", icon="⚠️")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.host_page = "main"
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create user: {message}")
        
        if cancel:
            st.session_state.host_page = "main"
            st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def delete_user_page():
    """Delete user account"""
    st.markdown("<h2 style='color:#D0021B;'>Delete Users</h2>", unsafe_allow_html=True)
    users = load_users()

    if not users:
        st.info("No users found in the system")
    else:
        search_query = st.text_input(
            "Search by User ID or Mobile Number",
            placeholder="Type user id or phone number",
            key="delete_user_search"
        ).strip().lower()

        user_rows = []
        for uid, user_info in users.items():
            profile = user_info.get("profile", {})
            phone = str(profile.get("phone", "") or "")
            if search_query and search_query not in uid.lower() and search_query not in phone.lower():
                continue
            user_rows.append({
                "User ID": uid,
                "Email": user_info.get("email", "N/A"),
                "Mobile": phone if phone else "N/A",
                "Name": profile.get("name", "N/A"),
                "City": profile.get("city", "N/A")
            })

        if not user_rows:
            st.warning("No users match your search")
        else:
            st.dataframe(user_rows, use_container_width=True, hide_index=True)

            selectable_user_ids = [row["User ID"] for row in user_rows]
            selected_user_ids = st.multiselect(
                "Select users to delete",
                options=selectable_user_ids,
                key="delete_user_multi_select"
            )

            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("🗑️ Delete Selected Users", use_container_width=True, key="confirm_delete_users", disabled=not selected_user_ids):
                    total_removed_applications = 0
                    total_removed_files = 0
                    deleted_count = 0

                    with st.spinner("Deleting selected users..."):
                        for uid in selected_user_ids:
                            if uid not in users:
                                continue
                            removed_apps, removed_files = cleanup_user_related_data(uid, users)
                            total_removed_applications += removed_apps
                            total_removed_files += len(removed_files)
                            del users[uid]
                            deleted_count += 1

                        save_users(users)
                        time.sleep(0.4)

                    st.success(f"✅ Deleted {deleted_count} user(s) successfully")
                    st.info(f"🧹 Cleanup: {total_removed_applications} application record(s), {total_removed_files} file(s)")
                    st.rerun()

            with c2:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_users"):
                    st.session_state.host_page = "main"
                    st.rerun()
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.host_page = "main"
        st.rerun()

def job_detail_page():
    """Detailed job and candidates view"""
    jobs = load_jobs()
    job_id = st.session_state.selected_job_id
    
    if not job_id or job_id not in jobs:
        st.error("Job not found")
        st.session_state.selected_job_id = None
        st.rerun()
        return
    
    job_info = jobs[job_id]
    applications = get_applications_by_job(job_id)
    
    # Back button
    if st.button("⬅️ Back to Jobs", use_container_width=False):
        st.session_state.selected_job_id = None
        st.rerun()
    
    # Job header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(168, 213, 186, 0.1), rgba(168, 213, 186, 0.05)); 
                border-left: 4px solid #A8D5BA; border-radius: 12px; padding: 20px; margin: 16px 0;'>
        <h2 style='color:#A8D5BA; margin:0;'>{job_info['title']}</h2>
        <p style='color:#b0b0b0; margin: 8px 0 0 0;'>{job_id} • {job_info.get('location', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Job metrics
    st.markdown("<h4 style='color:#A8D5BA;'>📊 Job Metrics</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Applications", len(applications))
    with col2:
        shortlisted = sum(1 for app in applications.values() if app.get('status') == 'Shortlisted')
        st.metric("⭐ Shortlisted", shortlisted)
    with col3:
        reviewed = sum(1 for app in applications.values() if app.get('score') is not None)
        st.metric("✓ Analyzed", reviewed)
    with col4:
        avg_score = sum(app.get('score', 0) for app in applications.values()) / len(applications) if applications else 0
        st.metric("📊 Avg Score", f"{avg_score:.1f}")
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Job description
    st.markdown("<h4 style='color:#A8D5BA;'>📝 Job Description</h4>", unsafe_allow_html=True)
    st.write(job_info.get('description', 'N/A'))
    
    if job_info.get('keywords'):
        st.markdown("<h4 style='color:#A8D5BA;'>🏷️ Required Skills</h4>", unsafe_allow_html=True)
        skills_html = " ".join([f"<span style='background: rgba(168, 213, 186, 0.15); padding: 4px 12px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 13px;'>{k.strip()}</span>" for k in job_info.get('keywords', [])])
        st.markdown(skills_html, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Candidates section
    st.markdown("<h3 style='color:#A8D5BA;'>👥 Applicants</h3>", unsafe_allow_html=True)
    
    if not applications:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">👤</div>
            <p>No candidates have applied yet</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            status_filter = st.selectbox("Filter by Status", ["All", "Applied", "Under Review", "Shortlisted", "Rejected"])
        with col_f2:
            score_filter = st.selectbox("Filter by Score", ["All", "≥70 (Excellent)", "50-70 (Good)", "<50 (Needs Review)"])
        with col_f3:
            sort_by = st.selectbox("Sort by", ["Match Score ↓", "Date Applied ↓"])
        
        # Apply filters
        filtered_apps = applications.copy()
        
        if status_filter != "All":
            filtered_apps = {k: v for k, v in filtered_apps.items() if v.get('status', 'Applied') == status_filter}
        
        if score_filter == "≥70 (Excellent)":
            filtered_apps = {k: v for k, v in filtered_apps.items() if v.get('score') and v['score'] >= 70}
        elif score_filter == "50-70 (Good)":
            filtered_apps = {k: v for k, v in filtered_apps.items() if v.get('score') and 50 <= v['score'] < 70}
        elif score_filter == "<50 (Needs Review)":
            filtered_apps = {k: v for k, v in filtered_apps.items() if v.get('score') is None or v['score'] < 50}
        
        if sort_by == "Match Score ↓":
            filtered_apps = dict(sorted(filtered_apps.items(), key=lambda x: x[1].get('score') or 0, reverse=True))
        
        if not filtered_apps:
            st.info("No candidates match the selected filters.")
        else:
            st.markdown(f"**Showing {len(filtered_apps)} of {len(applications)} candidates**")
            
            for user_id, info in filtered_apps.items():
                status = info.get('status', 'Applied')
                score = info.get('score')
                
                # Status color mapping
                status_class_map = {
                    'Applied': 'status-applied',
                    'Under Review': 'status-review',
                    'Shortlisted': 'status-shortlisted',
                    'Rejected': 'status-rejected'
                }
                status_class = status_class_map.get(status, 'status-applied')
                
                # Score display
                if score is None:
                    score_display = "⏳ Pending"
                    score_class = ""
                elif score >= 70:
                    score_display = f"🟢 {score}/100 Excellent"
                    score_class = "score-excellent"
                elif score >= 50:
                    score_display = f"🟡 {score}/100 Good"
                    score_class = "score-good"
                else:
                    score_display = f"🔴 {score}/100 Needs Review"
                    score_class = "score-poor"
                
                st.markdown(f"""
                <div class="candidate-card">
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                        <div>
                            <h5 style='color: #A8D5BA; margin: 0;'>👤 {user_id}</h5>
                            <small style='color: #999;'>Applied: {info.get('applied_at', 'N/A')[:10]}</small>
                        </div>
                        <span class='status-badge {status_class}'>{status}</span>
                    </div>
                    <div style='display: flex; gap: 20px;'>
                        <div><small style='color: #999;'>Match Score</small><br><span class='{score_class}'>{score_display}</span></div>
                        <div><small style='color: #999;'>Resume</small><br><span style='font-size: 13px;'>{info.get('resume', 'N/A')}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if st.button(f"🔍 Analyze Resume", key=f"analyze_{job_id}_{user_id}", use_container_width=True):
                        resume_path = info.get("resume")
                        
                        if not resume_path or not os.path.exists(resume_path):
                            st.error("❌ Resume not found")
                        else:
                            with st.spinner("🤖 Analyzing with AI..."):
                                resume_text = extract_text_from_pdf(resume_path)
                                details = get_match_details(resume_text, job_info.get('description', ''))
                                update_score(job_id, user_id, details['score'])
                                time.sleep(0.5)
                            
                            st.success(f"✅ Score: {details['score']}/100")
                            if details.get('matched_keywords'):
                                st.write(f"**Matched Skills:** {', '.join(details['matched_keywords'][:5])}")
                            st.rerun()
                
                with btn_col2:
                    status_options = ["Applied", "Under Review", "Shortlisted", "Rejected"]
                    new_status = st.selectbox(
                        "Update Status",
                        status_options,
                        index=status_options.index(status),
                        key=f"status_{job_id}_{user_id}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status and st.button(f"💾 Save", key=f"save_{job_id}_{user_id}", use_container_width=True):
                        update_status(job_id, user_id, new_status)
                        st.success(f"✅ Updated to {new_status}")
                        time.sleep(1)
                        st.rerun()
                
                with btn_col3:
                    if st.button(f"💬 Message", key=f"msg_{job_id}_{user_id}", use_container_width=True):
                        host_id = st.session_state.get("current_host_id") or st.session_state.get("host_id") or "host"
                        st.session_state.current_host_conversation = get_conversation_id(user_id, host_id, job_id)
                        st.session_state.host_chat_page = "chat"
                        st.session_state.host_page = "messages"
                        st.rerun()
                
                st.markdown("")

def main_dashboard_page():
    """Main dashboard command center"""
    jobs = load_jobs()
    users = load_users()
    applications = load_applications_data()

    total_jobs = len(jobs)
    total_users = len(users)
    total_apps = sum(len(apps) for apps in applications.values())
    analyzed_apps = sum(1 for apps in applications.values() for info in apps.values() if info.get("score") is not None)
    shortlisted_apps = sum(1 for apps in applications.values() for info in apps.values() if info.get("status") == "Shortlisted")
    interview_apps = sum(1 for apps in applications.values() for info in apps.values() if info.get("status") == "Interview")
    avg_score = 0
    scored = [info.get("score") for apps in applications.values() for info in apps.values() if info.get("score") is not None]
    if scored:
        avg_score = round(sum(scored) / len(scored), 1)
    jobs_without_apps = sum(1 for job_id in jobs.keys() if len(applications.get(job_id, {})) == 0)

    top_job_id = None
    top_job_apps = 0
    for job_id in jobs.keys():
        app_count = len(applications.get(job_id, {}))
        if app_count > top_job_apps:
            top_job_apps = app_count
            top_job_id = job_id
    top_job_title = jobs[top_job_id]["title"] if top_job_id and top_job_id in jobs else "N/A"

    analysis_rate = round((analyzed_apps / total_apps * 100), 1) if total_apps else 0
    shortlist_rate = round((shortlisted_apps / total_apps * 100), 1) if total_apps else 0

    st.markdown("""
    <style>
    .analog-board {
        background: linear-gradient(145deg, rgba(70, 52, 35, 0.55), rgba(34, 27, 19, 0.76));
        border: 2px solid rgba(211, 166, 102, 0.45);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: inset 0 2px 0 rgba(255,255,255,0.08), 0 12px 26px rgba(0,0,0,0.34);
    }
    .analog-chip {
        display: inline-block;
        background: rgba(0,0,0,0.35);
        border: 1px solid rgba(255, 216, 150, 0.35);
        color: #FFDDAA;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
        margin-top: 8px;
    }
    .analog-gauge-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(120px, 1fr));
        gap: 12px;
        margin-bottom: 10px;
    }
    .analog-gauge {
        background: linear-gradient(165deg, rgba(20,20,20,0.72), rgba(10,10,10,0.88));
        border: 1px solid rgba(255, 214, 144, 0.3);
        border-radius: 14px;
        padding: 10px;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1);
    }
    .analog-gauge-ring {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        margin: 0 auto 6px auto;
        border: 4px solid rgba(255, 205, 120, 0.45);
        box-shadow: inset 0 0 0 5px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFE4B8;
        font-weight: 800;
        font-size: 14px;
    }
    .analog-label {
        color: #D8C6A8;
        font-size: 11px;
        letter-spacing: 0.8px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .analog-sub {
        color: #B79F7D;
        font-size: 10px;
    }
    .analog-lamp {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #FFDCA8;
        font-weight: 700;
    }
    .analog-lamp i {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #7DFF88;
        display: inline-block;
        box-shadow: 0 0 8px #7DFF88;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='analog-board'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; margin-bottom:12px;'>
            <div>
                <h2 style='margin:0; color:#FFE0B0;'>HOST OPERATIONS COMMAND CENTER</h2>
                <p style='margin:6px 0 0 0; color:#D8C6A8;'>Analog control-board mode with live hiring telemetry.</p>
                <span class='analog-chip'>RETRO ANALOG SYSTEM</span>
            </div>
            <div style='text-align:right;'>
                <div class='analog-lamp'><i></i> POWER ONLINE</div>
                <div style='font-size:13px; color:#FFF2D8; margin-top:6px;'>{datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>
            </div>
        </div>
        <div class='analog-gauge-grid'>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{total_jobs}</div>
                <div class='analog-label'>Total Jobs</div>
                <div class='analog-sub'>Published Roles</div>
            </div>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{total_users}</div>
                <div class='analog-label'>Total Users</div>
                <div class='analog-sub'>Candidate Accounts</div>
            </div>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{total_apps}</div>
                <div class='analog-label'>Applications</div>
                <div class='analog-sub'>Inbound Flow</div>
            </div>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{analysis_rate}%</div>
                <div class='analog-label'>Analyzed</div>
                <div class='analog-sub'>{analyzed_apps}/{total_apps if total_apps else 0}</div>
            </div>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{shortlist_rate}%</div>
                <div class='analog-label'>Shortlisted</div>
                <div class='analog-sub'>{shortlisted_apps} qualified</div>
            </div>
            <div class='analog-gauge'>
                <div class='analog-gauge-ring'>{avg_score}</div>
                <div class='analog-label'>Avg Score</div>
                <div class='analog-sub'>AI Match Index</div>
            </div>
        </div>
        <div style='color:#CDBA9A; font-size:12px;'>Top demand job: <b>{top_job_title}</b> ({top_job_apps} applications)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#A8D5BA; font-size:18px;'>🚀 Quick Actions</h3>", unsafe_allow_html=True)

    def render_action_card(icon, title, subtitle, gradient, border):
        st.markdown(f"""
        <div style='background:{gradient}; border-left:4px solid {border}; border-radius:12px; padding:16px; margin:8px 0; text-align:center; min-height:102px;'>
            <h3 style='color:{border}; margin: 0; font-size: 28px;'>{icon}</h3>
            <p style='color:#d2d2d2; margin: 8px 0 0 0; font-weight: 600;'>{title}</p>
            <p style='color:#8fa0b2; margin: 3px 0 0 0; font-size: 12px;'>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        render_action_card("➕", "Create Job", "Launch new hiring role", "linear-gradient(135deg, rgba(168,213,186,0.20), rgba(168,213,186,0.06))", "#A8D5BA")
        if st.button("Create Job", use_container_width=True, key="quick_create"):
            st.session_state.host_page = "create_job"
            st.rerun()
    with col2:
        render_action_card("👥", "View Users", "Review candidate profiles", "linear-gradient(135deg, rgba(123,182,255,0.20), rgba(123,182,255,0.06))", "#7BB6FF")
        if st.button("View Users", use_container_width=True, key="quick_users"):
            st.session_state.host_page = "view_users"
            st.rerun()
    with col3:
        render_action_card("🤖", "Analyze All", "Run AI scoring pipeline", "linear-gradient(135deg, rgba(168,85,247,0.20), rgba(168,85,247,0.06))", "#B08CFF")
        if st.button("Analyze All", use_container_width=True, key="quick_analyze"):
            st.session_state.host_page = "analyse_all"
            st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        render_action_card("💬", "Messages", "Talk with candidates", "linear-gradient(135deg, rgba(54,211,153,0.20), rgba(54,211,153,0.06))", "#5BDFAE")
        if st.button("View Messages", use_container_width=True, key="quick_msg"):
            st.session_state.host_page = "messages"
            st.rerun()
    with col5:
        render_action_card("👤➕", "Create User", "Add managed user account", "linear-gradient(135deg, rgba(255,193,122,0.20), rgba(255,193,122,0.06))", "#FFC17A")
        if st.button("Create User", use_container_width=True, key="quick_create_user"):
            st.session_state.host_page = "create_user"
            st.rerun()
    with col6:
        render_action_card("👤🗑️", "Delete User", "Manage account removals", "linear-gradient(135deg, rgba(255,107,107,0.20), rgba(255,107,107,0.06))", "#FF6B6B")
        if st.button("Delete User", use_container_width=True, key="quick_delete_user"):
            st.session_state.host_page = "delete_user"
            st.rerun()

    col7, col8 = st.columns(2)
    with col7:
        render_action_card("🗑️", "Delete Job", "Remove archived positions", "linear-gradient(135deg, rgba(255,107,107,0.20), rgba(255,107,107,0.06))", "#FF6B6B")
        if st.button("Delete Job", use_container_width=True, key="quick_delete"):
            st.session_state.host_page = "delete_job"
            st.rerun()
    with col8:
        render_action_card("📋", "Your Job Postings", "Open all active positions", "linear-gradient(135deg, rgba(123,182,255,0.20), rgba(123,182,255,0.06))", "#7BB6FF")
        if st.button("Your Job Postings", use_container_width=True, key="quick_job_postings"):
            st.session_state.host_page = "job_postings"
            st.rerun()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#A8D5BA; font-size:18px;'>🧠 AI Insights</h3>", unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(f"""
        <div class='filter-box'>
            <div style='color:#9EC5F8; font-size:12px; font-weight:700;'>TOP DEMAND JOB</div>
            <div style='color:#FFFFFF; font-size:16px; font-weight:700; margin-top:6px;'>{top_job_title}</div>
            <div style='color:#9EAFC0; font-size:12px; margin-top:5px;'>Applications: {top_job_apps}</div>
        </div>
        """, unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class='filter-box'>
            <div style='color:#9EC5F8; font-size:12px; font-weight:700;'>PIPELINE ALERT</div>
            <div style='color:#FFFFFF; font-size:16px; font-weight:700; margin-top:6px;'>{jobs_without_apps} Jobs Need Applicants</div>
            <div style='color:#9EAFC0; font-size:12px; margin-top:5px;'>Focus promotion on low-traffic jobs</div>
        </div>
        """, unsafe_allow_html=True)
    with i3:
        st.markdown(f"""
        <div class='filter-box'>
            <div style='color:#9EC5F8; font-size:12px; font-weight:700;'>INTERVIEW READINESS</div>
            <div style='color:#FFFFFF; font-size:16px; font-weight:700; margin-top:6px;'>{interview_apps} In Interview Stage</div>
            <div style='color:#9EAFC0; font-size:12px; margin-top:5px;'>Shortlisted: {shortlisted_apps} candidates</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("⬅️ Back to Roles", use_container_width=True):
        st.session_state.page = "role"
        st.session_state.host_page = "main"
        st.rerun()


def job_postings_page():
    """Dedicated page for job postings"""
    st.markdown("<h3 style='color:#A8D5BA; font-size:20px;'>📋 Your Job Postings</h3>", unsafe_allow_html=True)

    jobs = load_jobs()

    if not jobs:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <p>No job postings yet</p>
            <p style='font-size: 13px; color: #666;'>Click "New Job" in Quick Actions to create your first posting</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_apps = sum(len(get_applications_by_job(job_id)) for job_id in jobs.keys())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💼 Active Jobs", len(jobs))
        with col2:
            st.metric("📨 Total Applications", total_apps)
        with col3:
            avg_apps = total_apps / len(jobs) if jobs else 0
            st.metric("📊 Avg per Job", f"{avg_apps:.1f}")

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        for job_id, job_info in jobs.items():
            applications = get_applications_by_job(job_id)
            shortlisted = sum(1 for app in applications.values() if app.get('status') == 'Shortlisted')
            analyzed = sum(1 for app in applications.values() if app.get('score') is not None)

            st.markdown(f"""
            <div class="job-card">
                <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;'>
                    <div style='flex: 1;'>
                        <h4 style='color: #A8D5BA; margin: 0 0 4px 0;'>{job_info['title']}</h4>
                        <p style='color: #999; margin: 0 0 8px 0; font-size: 13px;'>📍 {job_info.get('location', 'N/A')}</p>
                        <p style='color: #d0d0d0; margin: 0; font-size: 13px; line-height: 1.4;'>{job_info.get('description', 'N/A')[:120]}...</p>
                    </div>
                    <div style='text-align: right; margin-left: 20px;'>
                        <div style='font-size: 20px; font-weight: 700; color: #A8D5BA;'>{len(applications)}</div>
                        <div style='font-size: 12px; color: #999;'>Applications</div>
                        <div style='margin-top: 8px; font-size: 12px;'>
                            <div style='color: #7ED321;'>⭐ {shortlisted} Shortlisted</div>
                            <div style='color: #F5A623;'>✓ {analyzed} Analyzed</div>
                        </div>
                    </div>
                </div>
                <small style='color: #666;'>Job ID: {job_id}</small>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"👁️ View & Manage → {job_info['title']}", key=f"view_job_{job_id}", use_container_width=True):
                st.session_state.selected_job_id = job_id
                st.session_state.host_page = "job_detail"
                st.rerun()

            st.markdown("")

    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_from_job_postings"):
        st.session_state.host_page = "main"
        st.rerun()
