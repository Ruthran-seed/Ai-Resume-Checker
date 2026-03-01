import json
import os
import random
import string
from datetime import datetime

USER_FILE = "users.json"

# ================= LOAD USERS =================
def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: {USER_FILE} is corrupted")
            return {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    return {}

# ================= SAVE USERS =================
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ================= GENERATORS =================
def generate_user_id():
    return "USER" + str(random.randint(1000, 9999))

def generate_password():
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=8)
    )

# ================= VALIDATION FUNCTIONS =================
def validate_user_id(user_id):
    """Validate user ID format
    Returns: (is_valid, error_message)
    """
    user_id = user_id.strip()
    
    if len(user_id) < 4:
        return False, "User ID must be at least 4 characters"
    if len(user_id) > 15:
        return False, "User ID must be maximum 15 characters"
    if not user_id.replace("_", "").isalnum():
        return False, "User ID can only contain letters, numbers, and underscores"
    
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

# ================= CREATE USER =================
def create_user(email, user_id, password):
    """Create user with custom user_id and password
    Returns: (user_id, password) if successful, (None, error_message) if failed
    """
    email = email.strip().lower()
    user_id = user_id.strip()
    password = password.strip()
    
    # Validate user_id
    is_valid_id, id_error = validate_user_id(user_id)
    if not is_valid_id:
        return None, id_error
    
    # Validate password
    is_valid_pwd, pwd_error = validate_password(password)
    if not is_valid_pwd:
        return None, pwd_error
    
    users = load_users()
    
    # Check if email already exists
    for u in users.values():
        if u.get("email") == email:
            return None, "Email already registered"
    
    # Check if user_id already exists
    if user_id in users:
        return None, "User ID already taken"
    
    users[user_id] = {
        "email": email,
        "password": password,
        "role": "user",
        "profile_completed": False,
        "profile": {},
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    return user_id, password

# ================= LOGIN =================
def login_with_credentials(user_id, password):
    user_id = user_id.strip()  # Remove any whitespace
    password = password.strip()  # Remove any whitespace
    
    users = load_users()
    
    # Check if user exists and password matches
    if user_id in users:
        if users[user_id]["password"] == password:
            return users[user_id]
    
    return None

# ================= PROFILE FUNCTIONS =================
def save_user_profile(user_id, profile_data):
    users = load_users()

    if user_id not in users:
        return False

    users[user_id]["profile"] = profile_data
    users[user_id]["profile_completed"] = True
    save_users(users)
    return True

def get_user_profile(user_id):
    users = load_users()
    return users.get(user_id, {}).get("profile", {})

def is_profile_completed(user_id):
    users = load_users()
    return users.get(user_id, {}).get("profile_completed", False)

def user_exists(user_id):
    """Check if a user ID exists in the system"""
    users = load_users()
    return user_id in users

def get_user_existence_info(user_id):
    """Get info about whether a user exists (for debugging)"""
    users = load_users()
    user_id = user_id.strip()
    
    if user_id in users:
        return True, users[user_id].get("email", "Unknown")
    return False, None

# ================= PASSWORD MANAGEMENT =================
def get_user_email(user_id):
    """Get email address for a user ID"""
    users = load_users()
    if user_id in users:
        return users[user_id].get("email")
    return None

def change_password(user_id, old_password, new_password):
    """Change password for a user
    Returns: True if successful, False if old password is incorrect
    """
    users = load_users()
    
    if user_id not in users:
        return False
    
    # Verify old password is correct
    if users[user_id]["password"] != old_password.strip():
        return False
    
    # Update password
    users[user_id]["password"] = new_password.strip()
    save_users(users)
    return True

def reset_password_by_email(email):
    """Reset password by email address
    Returns: (user_id, new_password) if successful, (None, None) if email not found
    """
    email = email.strip().lower()
    users = load_users()
    
    # Find user by email
    for user_id, user_data in users.items():
        if user_data.get("email") == email:
            # Generate new password
            new_password = generate_password()
            # Update password
            users[user_id]["password"] = new_password
            save_users(users)
            return user_id, new_password
    
    return None, None
