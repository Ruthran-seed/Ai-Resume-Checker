# 💬 Chat Feature Documentation

## Overview
The chat feature allows **Job Seekers (Users)** and **Employers (Hosts)** to communicate directly within the AI Resume Checker platform.

---

## Features

### For Job Seekers (Users)
✅ **View all conversations** with employers  
✅ **Send and receive messages** from hosts  
✅ **Search conversations** by host ID or message content  
✅ **Delete conversations** when no longer needed  
✅ **Unread message counter** for quick notifications  
✅ **Real-time message timestamps**  

### For Employers (Hosts)
✅ **Manage conversations** with multiple candidates  
✅ **Quick messaging** from application review page  
✅ **Search candidate conversations** by ID or message  
✅ **Unread message tracking** for follow-ups  
✅ **Track all candidate interactions** in one place  

---

## How to Use

### Job Seeker (User) - Accessing Chat

1. **Login** to your job seeker account
2. Go to **Dashboard**
3. Click **💬 Messages**
4. You'll see:
   - **My Conversations** - List of all chats with employers
   - **Unread Badge** - Shows new message count
   - **Search Bar** - Search conversations by host ID or message content

### Starting a Conversation
Conversations are **automatically created** when:
- A host sends you a message after reviewing your application
- You respond to a message from a host

### Sending a Message
1. Click on a conversation to open it
2. Type your message in the text box at the bottom
3. Click **📤 Send**
4. Your message appears on the right side (green background)

### Host Messages
- Messages from hosts appear on the **left side** (dark gray background)
- New messages are marked as **unread**
- All messages show **timestamps** for reference

---

### Employer (Host) - Accessing Chat

1. **Login** to your host/employer account
2. Go to **Host Dashboard**
3. You have **two ways** to access chat:

#### Method 1: View all Conversations
- Click **💬 Messages** button on the dashboard
- See all conversations with candidates
- Search by candidate ID or message content

#### Method 2: Message from Application Review
- While reviewing a candidate's application
- Click **💬 Send Message** button
- Chat window opens with that specific candidate
- Automatically creates conversation for that candidate

### Sending a Message to a Candidate
1. Open the candidate's conversation
2. Type your message in the text box
3. Click **📤 Send**
4. Your message appears on the right side (green background)

---

## File Structure

### New Files Created

#### 1. **chat_manager.py**
Core chat management module with functions:
- `send_message()` - Send a message in a conversation
- `get_messages()` - Retrieve all messages in a conversation
- `get_user_conversations()` - Get all conversations for a user
- `get_host_conversations()` - Get all conversations for a host
- `mark_as_read()` - Mark messages as read
- `count_unread_messages()` - Count unread messages
- `delete_conversation()` - Delete a conversation
- `search_conversations()` - Search conversations

#### 2. **user_chat.py**
Frontend interface for job seekers:
- `user_chat_interface()` - Main chat UI for users
- Inbox view with conversation list
- Chat view with message display
- Message input and sending

#### 3. **host_chat.py**
Frontend interface for employers:
- `host_chat_interface()` - Main chat UI for hosts
- Conversation inbox with candidate list
- Chat view with message threads
- Quick messaging from applications

### Modified Files

#### **app.py**
- Added imports for chat modules
- Added "💬 Messages" button to user dashboard
- Added user_chat page routing
- Set `current_host_id` on host login

#### **host_panel.py**
- Added import for host_chat
- Added "💬 Messages" button to host dashboard
- Added "💬 Send Message" button to candidate review
- Added messages page handling

---

## Data Storage

### Chat Storage (chats.json)
```json
{
  "HOST_ID_JOB_ID_USER_ID": {
    "participants": {
      "host_id": "HOST123",
      "user_id": "USER456"
    },
    "messages": [
      {
        "sender_id": "HOST123",
        "sender_type": "host",
        "message": "Hi, we're interested in your profile!",
        "timestamp": "2026-02-09T10:30:45.123456",
        "read": true
      },
      {
        "sender_id": "USER456",
        "sender_type": "user",
        "message": "Thank you! I'm very interested.",
        "timestamp": "2026-02-09T10:35:12.654321",
        "read": true
      }
    ],
    "created_at": "2026-02-09T10:30:45.123456"
  }
}
```

---

## Key Improvements

1. **Professional Communication** - Direct messaging between candidates and employers
2. **Better User Experience** - All interactions in one place
3. **Message Tracking** - Know when messages are read
4. **Quick Access** - Message button directly from application review
5. **Search Functionality** - Easily find past conversations
6. **Responsive Design** - Works across all devices

---

## Future Enhancement Ideas

- 📎 **File Attachments** - Share documents in chat
- 🔔 **Notifications** - Real-time message alerts
- 📅 **Scheduled Messages** - Send messages at specific times
- ⭐ **Message Reactions** - React with emojis
- 🤖 **AI Suggestions** - Smart message templates
- 📞 **Video Calls** - Integrate video calling
- 💾 **Message Export** - Download chat history

---

## Testing the Chat Feature

### Test Case 1: User to Host Communication
1. Create a user account
2. Upload a resume
3. Apply for a job
4. Login as host and review application
5. Click "💬 Send Message" and send a message
6. Login as user and check "💬 Messages"
7. Verify message appears and send a reply

### Test Case 2: Search Functionality
1. Create multiple conversations
2. Use the search bar to find specific conversations
3. Search by host/user ID
4. Search by message content

### Test Case 3: Unread Messages
1. Send message from host
2. Verify unread count appears for user
3. Open conversation
4. Verify unread count goes to 0

---

## Troubleshooting

### Problem: Messages not appearing
- **Solution**: Refresh the page (F5) or click the 🔄 Refresh button

### Problem: Cannot find conversation
- **Solution**: Use the search bar to find conversations by ID or message content
- **Note**: Conversations only appear after at least one message is sent

### Problem: Message not sending
- **Solution**: 
  - Check that your message is not empty
  - Make sure you're logged in
  - Verify internet connection

### Problem: Unread count not updating
- **Solution**: Refresh the page to sync the latest message status

---

## Support

For issues or questions about the chat feature:
1. Check this documentation
2. Verify both parties have logged in successfully
3. Ensure the chats.json file exists in the application directory
4. Contact support: support@airesume.example
