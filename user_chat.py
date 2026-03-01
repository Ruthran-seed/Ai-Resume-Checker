import streamlit as st
import json
import os
from datetime import datetime
from chat_manager import (
    get_conversation_id,
    send_message,
    get_messages,
    get_user_conversations,
    mark_as_read,
    count_unread_messages,
    delete_conversation
)
from auth import get_user_profile

# ================= USER CHAT INTERFACE =================
def user_chat_interface():
    """Chat interface for job seekers"""
    
    # Initialize chat state
    if "user_chat_page" not in st.session_state:
        st.session_state.user_chat_page = "inbox"
    
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = None
    
    st.markdown("<h2 style='color:#7BB6FF;'>💬 Messages</h2>", unsafe_allow_html=True)
    
    # -------- INBOX PAGE --------
    if st.session_state.user_chat_page == "inbox":
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("<h3>My Conversations</h3>", unsafe_allow_html=True)
        with col2:
            unread_count = count_unread_messages(st.session_state.user_id, "user")
            if unread_count > 0:
                st.markdown(f"<span style='color:#FF6B6B; font-weight:bold;'>New Messages: {unread_count}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        conversations = get_user_conversations(st.session_state.user_id)
        
        if not conversations:
            st.info("📭 No conversations yet. Apply for jobs and hosts will start messaging you!")
        else:
            # Search conversations
            search_query = st.text_input("🔍 Search conversations...", placeholder="Search by host ID or message content")
            
            if search_query:
                from chat_manager import search_conversations
                conversations = search_conversations(st.session_state.user_id, "user", search_query)
            
            if not conversations and search_query:
                st.info("No conversations found matching your search")
            else:
                for conv in conversations:
                    # Get unread status for this conversation
                    messages = get_messages(conv["conversation_id"])
                    unread_in_conv = sum(1 for m in messages if not m["read"] and m["sender_type"] == "host")
                    
                    # Format the conversation display
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        conv_label = f"🏢 **{conv['host_id']}**"
                        if unread_in_conv > 0:
                            conv_label += f" ({unread_in_conv} new)"
                        
                        if st.button(conv_label, use_container_width=True, key=f"open_{conv['conversation_id']}"):
                            st.session_state.current_conversation = conv['conversation_id']
                            mark_as_read(conv['conversation_id'], "user")
                            st.session_state.user_chat_page = "chat"
                            st.rerun()
                    
                    with col2:
                        st.caption(conv['last_message'][:30] + "..." if len(conv['last_message']) > 30 else conv['last_message'])
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{conv['conversation_id']}", help="Delete conversation"):
                            delete_conversation(conv['conversation_id'])
                            st.rerun()
                    
                    st.markdown("---")
    
    # -------- CHAT PAGE --------
    elif st.session_state.user_chat_page == "chat":
        if not st.session_state.current_conversation:
            st.error("No conversation selected")
            if st.button("⬅️ Back to Inbox"):
                st.session_state.user_chat_page = "inbox"
                st.session_state.current_conversation = None
                st.rerun()
            return
        
        # Get conversation details
        conversations = get_user_conversations(st.session_state.user_id)
        current_conv = None
        for conv in conversations:
            if conv['conversation_id'] == st.session_state.current_conversation:
                current_conv = conv
                break
        
        if not current_conv:
            st.error("Conversation not found")
            if st.button("⬅️ Back to Inbox"):
                st.session_state.user_chat_page = "inbox"
                st.session_state.current_conversation = None
                st.rerun()
            return
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<h3>💬 Chat with {current_conv['host_id']}</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("⬅️ Back to Inbox"):
                st.session_state.user_chat_page = "inbox"
                st.session_state.current_conversation = None
                st.rerun()
        
        st.markdown("---")
        
        # Display messages
        messages = get_messages(st.session_state.current_conversation)
        
        if messages:
            for msg in messages:
                if msg['sender_type'] == 'user':
                    # User's message (right side)
                    st.markdown(f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div style='background: #2F6FB8; color: white; padding: 10px 15px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <p style='margin: 0;'>{msg['message']}</p>
                            <small style='color: #a0a0a0; font-size: 11px;'>{msg['timestamp'].split('T')[1][:5]}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Host's message (left side)
                    st.markdown(f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div style='background: #2d3748; color: white; padding: 10px 15px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <p style='margin: 0;'>{msg['message']}</p>
                            <small style='color: #a0a0a0; font-size: 11px;'>{msg['timestamp'].split('T')[1][:5]}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💭 No messages yet. Start the conversation!")
        
        st.markdown("---")
        
        # Message input
        col1, col2 = st.columns([5, 1])
        with col1:
            new_message = st.text_input("📝 Type your message...", placeholder="Write something...", key="user_message_input")
        with col2:
            send_btn = st.button("📤 Send", use_container_width=True)
        
        if send_btn and new_message.strip():
            send_message(
                sender_id=st.session_state.user_id,
                sender_type="user",
                receiver_id=current_conv['host_id'],
                message=new_message.strip(),
                conversation_id=st.session_state.current_conversation
            )
            st.success("✅ Message sent!")
            st.rerun()
        elif send_btn:
            st.warning("⚠️ Please type a message")

# ================= USER CHAT BUTTON FOR DASHBOARD =================
def add_user_chat_button():
    """Add chat button to user dashboard with modern styling"""
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(56, 116, 184, 0.18), rgba(123, 182, 255, 0.06));
        border-left: 4px solid #7BB6FF;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    '>
        <h3 style='color:#7BB6FF; margin: 0;'>💬 Messages</h3>
        <p style='color:#b0b0b0; margin: 8px 0 0 0;'>Chat with employers</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Open Messages", use_container_width=True, key="user_chat_btn"):
        st.session_state.page = "user_chat"
        st.rerun()

# ================= AI CHATBOT INTERFACE =================
def user_ai_chatbot_interface():
    """AI Chat interface for job seekers to ask queries"""
    
    # Initialize AI chat state
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    
    st.markdown("<h2 style='color:#7BB6FF;'>🤖 AI Career Assistant</h2>", unsafe_allow_html=True)
    st.markdown("Ask me anything about jobs, resumes, career development, and more!", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.ai_chat_history:
        for msg in st.session_state.ai_chat_history:
            if msg["type"] == "user":
                st.markdown(f"""
                <div style='text-align: right; margin: 12px 0;'>
                    <div style='background: #2F6FB8; color: white; padding: 12px 15px; border-radius: 15px; display: inline-block; max-width: 75%;'>
                        <p style='margin: 0;'>{msg["content"]}</p>
                        <small style='color: #a0a0a0; font-size: 11px;'>{msg.get("timestamp", "")}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align: left; margin: 12px 0;'>
                    <div style='background: #2d3748; color: white; padding: 12px 15px; border-radius: 15px; display: inline-block; max-width: 75%;'>
                        <p style='margin: 0;'>{msg["content"]}</p>
                        <small style='color: #a0a0a0; font-size: 11px;'>{msg.get("timestamp", "")}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👋 Start a conversation! Ask me about job applications, resume tips, interview preparation, or career advice.")
    
    st.markdown("---")
    
    # Chat input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_query = st.text_input("📝 Ask me something...", placeholder="e.g., How do I improve my resume? What skills are in demand?", key="ai_chat_input")
    with col2:
        send_btn = st.button("📤 Send", use_container_width=True)
    
    if send_btn and user_query.strip():
        from datetime import datetime
        from ai_chat import generate_ai_response
        
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.ai_chat_history.append({
            "type": "user",
            "content": user_query.strip(),
            "timestamp": timestamp
        })
        
        # Get AI response
        with st.spinner("🤔 AI Assistant is thinking..."):
            try:
                user_profile = get_user_profile(st.session_state.user_id) if "user_id" in st.session_state else None
                ai_response = generate_ai_response(
                    user_query.strip(),
                    sender_type="user",
                    user_profile=user_profile
                )
                
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.ai_chat_history.append({
                    "type": "assistant",
                    "content": ai_response,
                    "timestamp": timestamp
                })
                st.success("✅ Response received!")
            except Exception as e:
                st.error(f"Error getting AI response: {str(e)}")
        
        st.rerun()
    elif send_btn:
        st.warning("⚠️ Please ask a question")
    
    st.markdown("---")
    
    # Quick action buttons - Modern styled boxes
    st.markdown("<h4 style='color:#7BB6FF;'>💡 Quick Questions:</h4>", unsafe_allow_html=True)
    
    quick_questions = [
        ("✍️ Resume Tips", "How do I write a better resume?"),
        ("📊 In-Demand Skills", "What skills are in demand?"),
        ("🎤 Interview Tips", "Interview tips for tech jobs?")
    ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(56, 116, 184, 0.18), rgba(123, 182, 255, 0.06));
            border-left: 4px solid #7BB6FF;
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            text-align: center;
        '>
            <h3 style='color:#7BB6FF; margin: 0; font-size: 24px;'>✍️</h3>
            <p style='color:#b0b0b0; margin: 8px 0 0 0; font-weight: 500;'>Resume Tips</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask AI", use_container_width=True, key="q1_btn"):
            st.session_state.ai_chat_history.append({
                "type": "user",
                "content": quick_questions[0][1],
                "timestamp": datetime.now().strftime("%H:%M")
            })
            from ai_chat import generate_ai_response
            ai_response = generate_ai_response(quick_questions[0][1], sender_type="user")
            st.session_state.ai_chat_history.append({
                "type": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(56, 116, 184, 0.18), rgba(123, 182, 255, 0.06));
            border-left: 4px solid #7BB6FF;
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            text-align: center;
        '>
            <h3 style='color:#7BB6FF; margin: 0; font-size: 24px;'>📊</h3>
            <p style='color:#b0b0b0; margin: 8px 0 0 0; font-weight: 500;'>In-Demand Skills</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask AI", use_container_width=True, key="q2_btn"):
            st.session_state.ai_chat_history.append({
                "type": "user",
                "content": quick_questions[1][1],
                "timestamp": datetime.now().strftime("%H:%M")
            })
            from ai_chat import generate_ai_response
            ai_response = generate_ai_response(quick_questions[1][1], sender_type="user")
            st.session_state.ai_chat_history.append({
                "type": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(56, 116, 184, 0.18), rgba(123, 182, 255, 0.06));
            border-left: 4px solid #7BB6FF;
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            text-align: center;
        '>
            <h3 style='color:#7BB6FF; margin: 0; font-size: 24px;'>🎤</h3>
            <p style='color:#b0b0b0; margin: 8px 0 0 0; font-weight: 500;'>Interview Tips</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask AI", use_container_width=True, key="q3_btn"):
            st.session_state.ai_chat_history.append({
                "type": "user",
                "content": quick_questions[2][1],
                "timestamp": datetime.now().strftime("%H:%M")
            })
            from ai_chat import generate_ai_response
            ai_response = generate_ai_response(quick_questions[2][1], sender_type="user")
            st.session_state.ai_chat_history.append({
                "type": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            st.rerun()
    
    st.markdown("---")
    
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()