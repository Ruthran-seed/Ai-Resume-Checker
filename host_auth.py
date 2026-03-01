import json
import os
import random
import string
from datetime import datetime

HOST_FILE = "hosts.json"

# 🔑 SECRET KEY (ONLY YOU KNOW THIS)
ADMIN_SECRET_KEY = "AVATAR-HOST-2026"

# ---------- Helpers ----------
def load_hosts():
    if os.path.exists(HOST_FILE):
        try:
            with open(HOST_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: {HOST_FILE} is corrupted")
            return {}
        except Exception:
            return {}
    return {}

def save_hosts(hosts):
    with open(HOST_FILE, "w") as f:
        json.dump(hosts, f, indent=2)

def generate_host_id():
    return "HOST" + str(random.randint(1000, 9999))

def generate_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))

# ================= VALIDATION FUNCTIONS =================
def validate_host_id(host_id):
    """Validate host ID format
    Returns: (is_valid, error_message)
    """
    host_id = host_id.strip()
    
    if len(host_id) < 4:
        return False, "Host ID must be at least 4 characters"
    if len(host_id) > 15:
        return False, "Host ID must be maximum 15 characters"
    if not host_id.replace("_", "").isalnum():
        return False, "Host ID can only contain letters, numbers, and underscores"
    
    return True, ""

def validate_password(password):
    """Validate password strength
    Returns: (is_valid, error_message)
    """
    password = password.strip()
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 20:
        return False, "Password must be maximum 20 characters"
    
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, ""

# ---------- CREATE HOST ----------
def create_host(email, host_id, password, admin_key):
    """Create host with custom host_id and password
    Requires valid admin access key for security
    Returns: (host_id, password) if successful, (None, error_message) if failed
    """
    # Validate admin key first
    if not admin_key or admin_key.strip() != ADMIN_SECRET_KEY:
        return None, "❌ Invalid Admin Access Key"
    
    email = email.strip().lower()
    host_id = host_id.strip()
    password = password.strip()
    
    # Validate host_id
    is_valid_id, id_error = validate_host_id(host_id)
    if not is_valid_id:
        return None, id_error
    
    # Validate password
    is_valid_pwd, pwd_error = validate_password(password)
    if not is_valid_pwd:
        return None, pwd_error
    
    hosts = load_hosts()
    
    # Check if email already exists
    for h in hosts.values():
        if h.get("email") == email:
            return None, "Email already registered"
    
    # Check if host_id already exists
    if host_id in hosts:
        return None, "Host ID already taken"
    
    hosts[host_id] = {
        "email": email,
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    
    save_hosts(hosts)
    return host_id, password

# ---------- LOGIN HOST ----------
def login_host(host_id, password):
    hosts = load_hosts()
    if host_id in hosts and hosts[host_id]["password"] == password:
        return True
    return False
# ---------- HOST PASSWORD MANAGEMENT ----------
def reset_host_password_by_email(email):
    """Reset host password by email address
    Returns: (host_id, new_password) if successful, (None, None) if email not found
    """
    email = email.strip().lower()
    hosts = load_hosts()
    
    # Find host by email
    for host_id, host_data in hosts.items():
        if host_data.get("email") == email:
            # Generate new password following validation rules
            new_password = generate_password()
            # Update password
            hosts[host_id]["password"] = new_password
            save_hosts(hosts)
            return host_id, new_password
    
    return None, None

def change_host_password(host_id, old_password, new_password):
    """Change host password
    Returns: True if successful, False if old password is incorrect
    """
    hosts = load_hosts()
    
    if host_id not in hosts:
        return False
    
    # Verify old password is correct
    if hosts[host_id]["password"] != old_password.strip():
        return False
    
    # Validate new password
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        return False
    
    # Update password
    hosts[host_id]["password"] = new_password.strip()
    save_hosts(hosts)
    return True