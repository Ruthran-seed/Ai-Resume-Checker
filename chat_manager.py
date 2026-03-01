import json
import os
from datetime import datetime

CHAT_FILE = "chats.json"

# ================= LOAD CHATS =================
def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: {CHAT_FILE} is corrupted")
            return {}
        except Exception as e:
            print(f"Error loading chats: {e}")
            return {}
    return {}

# ================= SAVE CHATS =================
def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f, indent=2)

# ================= GET OR CREATE CONVERSATION =================
def get_conversation_id(user_id, host_id, job_id=None):
    """Generate a unique conversation ID"""
    if job_id:
        return f"{host_id}_{job_id}_{user_id}"
    return f"{host_id}_{user_id}"

# ================= SEND MESSAGE =================
def send_message(sender_id, sender_type, receiver_id, message, conversation_id):
    """Send a message in a conversation
    sender_type: 'user' or 'host'
    """
    chats = load_chats()
    
    if conversation_id not in chats:
        chats[conversation_id] = {
            "participants": {
                "host_id": receiver_id if sender_type == "user" else sender_id,
                "user_id": sender_id if sender_type == "user" else receiver_id,
            },
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    chats[conversation_id]["messages"].append({
        "sender_id": sender_id,
        "sender_type": sender_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })
    
    save_chats(chats)
    return True

# ================= GET MESSAGES =================
def get_messages(conversation_id):
    """Get all messages in a conversation"""
    chats = load_chats()
    
    if conversation_id not in chats:
        return []
    
    return chats[conversation_id]["messages"]

# ================= GET CONVERSATIONS FOR USER =================
def get_user_conversations(user_id):
    """Get all conversations for a specific user"""
    chats = load_chats()
    user_conversations = []
    
    for conv_id, conversation in chats.items():
        if conversation["participants"].get("user_id") == user_id:
            user_conversations.append({
                "conversation_id": conv_id,
                "host_id": conversation["participants"]["host_id"],
                "user_id": user_id,
                "created_at": conversation["created_at"],
                "last_message_count": len(conversation["messages"]),
                "last_message": conversation["messages"][-1]["message"] if conversation["messages"] else ""
            })
    
    return user_conversations

# ================= GET CONVERSATIONS FOR HOST =================
def get_host_conversations(host_id):
    """Get all conversations for a specific host"""
    chats = load_chats()
    host_conversations = []
    
    for conv_id, conversation in chats.items():
        if conversation["participants"].get("host_id") == host_id:
            host_conversations.append({
                "conversation_id": conv_id,
                "host_id": host_id,
                "user_id": conversation["participants"]["user_id"],
                "created_at": conversation["created_at"],
                "last_message_count": len(conversation["messages"]),
                "last_message": conversation["messages"][-1]["message"] if conversation["messages"] else ""
            })
    
    return host_conversations

# ================= MARK MESSAGES AS READ =================
def mark_as_read(conversation_id, reader_type):
    """Mark messages as read by a specific participant"""
    chats = load_chats()
    
    if conversation_id not in chats:
        return False
    
    for message in chats[conversation_id]["messages"]:
        # Mark unread messages from the other party as read
        if reader_type == "user" and message["sender_type"] == "host":
            message["read"] = True
        elif reader_type == "host" and message["sender_type"] == "user":
            message["read"] = True
    
    save_chats(chats)
    return True

# ================= COUNT UNREAD MESSAGES =================
def count_unread_messages(user_id, reader_type):
    """Count unread messages for a user"""
    chats = load_chats()
    unread_count = 0
    
    if reader_type == "user":
        conversations = get_user_conversations(user_id)
    else:
        conversations = get_host_conversations(user_id)
    
    for conv in conversations:
        messages = get_messages(conv["conversation_id"])
        for message in messages:
            if not message["read"]:
                if reader_type == "user" and message["sender_type"] == "host":
                    unread_count += 1
                elif reader_type == "host" and message["sender_type"] == "user":
                    unread_count += 1
    
    return unread_count

# ================= DELETE CONVERSATION =================
def delete_conversation(conversation_id):
    """Delete a conversation"""
    chats = load_chats()
    
    if conversation_id in chats:
        del chats[conversation_id]
        save_chats(chats)
        return True
    
    return False

# ================= SEARCH CONVERSATIONS =================
def search_conversations(user_id, user_type, search_query):
    """Search conversations based on participant ID or message content"""
    if user_type == "user":
        conversations = get_user_conversations(user_id)
    else:
        conversations = get_host_conversations(user_id)
    
    results = []
    search_lower = search_query.lower()
    
    for conv in conversations:
        other_id = conv["host_id"] if user_type == "user" else conv["user_id"]
        
        # Check if other participant matches
        if search_lower in other_id.lower():
            results.append(conv)
            continue
        
        # Check if any message contains the search term
        messages = get_messages(conv["conversation_id"])
        for msg in messages:
            if search_lower in msg["message"].lower():
                results.append(conv)
                break
    
    return results
# ================= AI CHAT RESPONSES =================
def get_ai_suggestion(conversation_id, context=""):
    """Get AI-suggested response for a conversation"""
    try:
        from ai_chat import generate_ai_response
        
        messages = get_messages(conversation_id)
        if not messages:
            return ""
        
        last_message = messages[-1]["message"]
        sender_type = messages[-1]["sender_type"]
        
        # Determine recipient type (opposite of sender)
        recipient_type = "host" if sender_type == "user" else "user"
        
        response = generate_ai_response(last_message, recipient_type, context)
        return response
    
    except Exception as e:
        print(f"Error getting AI suggestion: {e}")
        return ""

def send_ai_message(sender_id, sender_type, receiver_id, conversation_id, context=""):
    """Send an AI-generated message"""
    try:
        from ai_chat import generate_ai_response
        
        # Get the last user message
        messages = get_messages(conversation_id)
        if not messages:
            return False
        
        last_user_msg = None
        for msg in reversed(messages):
            if msg["sender_type"] != sender_type:
                last_user_msg = msg["message"]
                break
        
        if not last_user_msg:
            return False
        
        # Generate AI response
        ai_response = generate_ai_response(last_user_msg, sender_type, context)
        
        if ai_response:
            return send_message(sender_id, sender_type, receiver_id, ai_response, conversation_id)
    
    except Exception as e:
        print(f"Error sending AI message: {e}")
    
    return False