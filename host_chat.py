import streamlit as st
from chat_manager import (
    send_message,
    get_messages,
    get_host_conversations,
    mark_as_read,
    count_unread_messages,
    delete_conversation
)

# ================= HOST CHAT INTERFACE =================
def host_chat_interface():
    """Chat interface for employers/hosts"""
    
    # Initialize chat state
    if "host_chat_page" not in st.session_state:
        st.session_state.host_chat_page = "inbox"
    
    if "current_host_conversation" not in st.session_state:
        st.session_state.current_host_conversation = None
    
    if "current_host_id" not in st.session_state:
        st.session_state.current_host_id = None
    
    st.markdown("<h2 style='color:#A8D5BA;'>💬 Candidate Messages</h2>", unsafe_allow_html=True)
    
    # -------- INBOX PAGE --------
    if st.session_state.host_chat_page == "inbox":
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("<h3>Conversations with Candidates</h3>", unsafe_allow_html=True)
        with col2:
            unread_count = count_unread_messages(st.session_state.current_host_id, "host")
            if unread_count > 0:
                st.markdown(f"<span style='color:#FF6B6B; font-weight:bold;'>New Messages: {unread_count}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        conversations = get_host_conversations(st.session_state.current_host_id)
        
        if not conversations:
            st.info("📭 No conversations yet. Message candidates after reviewing their applications!")
        else:
            # Search conversations
            search_query = st.text_input("🔍 Search conversations...", placeholder="Search by candidate ID or message content")
            
            if search_query:
                from chat_manager import search_conversations
                conversations = search_conversations(st.session_state.current_host_id, "host", search_query)
            
            if not conversations and search_query:
                st.info("No conversations found matching your search")
            else:
                for conv in conversations:
                    # Get unread status for this conversation
                    messages = get_messages(conv["conversation_id"])
                    unread_in_conv = sum(1 for m in messages if not m["read"] and m["sender_type"] == "user")
                    
                    # Format the conversation display
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        conv_label = f"👤 **{conv['user_id']}**"
                        if unread_in_conv > 0:
                            conv_label += f" ({unread_in_conv} new)"
                        
                        if st.button(conv_label, use_container_width=True, key=f"host_open_{conv['conversation_id']}"):
                            st.session_state.current_host_conversation = conv['conversation_id']
                            mark_as_read(conv['conversation_id'], "host")
                            st.session_state.host_chat_page = "chat"
                            st.rerun()
                    
                    with col2:
                        st.caption(conv['last_message'][:30] + "..." if len(conv['last_message']) > 30 else conv['last_message'])
                    
                    with col3:
                        if st.button("🗑️", key=f"host_delete_{conv['conversation_id']}", help="Delete conversation"):
                            delete_conversation(conv['conversation_id'])
                            st.rerun()
                    
                    st.markdown("---")
    
    # -------- CHAT PAGE --------
    elif st.session_state.host_chat_page == "chat":
        if not st.session_state.current_host_conversation:
            st.error("No conversation selected")
            if st.button("⬅️ Back to Inbox"):
                st.session_state.host_chat_page = "inbox"
                st.session_state.current_host_conversation = None
                st.rerun()
            return
        
        # Get conversation details
        conversations = get_host_conversations(st.session_state.current_host_id)
        current_conv = None
        for conv in conversations:
            if conv['conversation_id'] == st.session_state.current_host_conversation:
                current_conv = conv
                break
        
        if not current_conv:
            st.error("Conversation not found")
            if st.button("⬅️ Back to Inbox"):
                st.session_state.host_chat_page = "inbox"
                st.session_state.current_host_conversation = None
                st.rerun()
            return
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<h3>💬 Chat with {current_conv['user_id']}</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("⬅️ Back to Inbox"):
                st.session_state.host_chat_page = "inbox"
                st.session_state.current_host_conversation = None
                st.rerun()
        
        st.markdown("---")
        
        # Display messages
        messages = get_messages(st.session_state.current_host_conversation)
        
        if messages:
            for msg in messages:
                if msg['sender_type'] == 'host':
                    # Host's message (right side)
                    st.markdown(f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div style='background: #1F6B4F; color: white; padding: 10px 15px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <p style='margin: 0;'>{msg['message']}</p>
                            <small style='color: #a0a0a0; font-size: 11px;'>{msg['timestamp'].split('T')[1][:5]}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Candidate's message (left side)
                    st.markdown(f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div style='background: #2d3748; color: white; padding: 10px 15px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <p style='margin: 0;'>{msg['message']}</p>
                            <small style='color: #a0a0a0; font-size: 11px;'>{msg['timestamp'].split('T')[1][:5]}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💭 Start the conversation with a message!")
        
        st.markdown("---")
        
        # Message input
        col1, col2 = st.columns([5, 1])
        with col1:
            new_message = st.text_input("📝 Type your message...", placeholder="Write something...", key="host_message_input")
        with col2:
            send_btn = st.button("📤 Send", use_container_width=True)
        
        if send_btn and new_message.strip():
            send_message(
                sender_id=st.session_state.current_host_id,
                sender_type="host",
                receiver_id=current_conv['user_id'],
                message=new_message.strip(),
                conversation_id=st.session_state.current_host_conversation
            )
            st.success("✅ Message sent!")
            st.rerun()
        elif send_btn:
            st.warning("⚠️ Please type a message")

# ================= HOST CHAT BUTTON FOR DASHBOARD =================
def add_host_chat_button():
    """Add chat button to host dashboard with modern styling"""
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(168, 213, 186, 0.15), rgba(168, 213, 186, 0.05));
        border-left: 4px solid #A8D5BA;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    '>
        <h3 style='color:#A8D5BA; margin: 0;'>💬 Candidate Messages</h3>
        <p style='color:#b0b0b0; margin: 8px 0 0 0;'>Communicate with applicants</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Open Messages", use_container_width=True, key="host_chat_btn"):
        st.session_state.host_page = "messages"
        st.rerun()
