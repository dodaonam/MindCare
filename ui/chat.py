import streamlit as st
import requests

st.set_page_config(
    page_title="Mental Health Chat",
    page_icon="🧠",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "sources_history" not in st.session_state:
    st.session_state.sources_history = {}  # Map message index to sources

with st.sidebar:
    st.header("💬 Quản lý hội thoại")
    
    # New conversation button
    if st.button("🆕 Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.sources_history = {}
        st.rerun()
    
    st.divider()
    
    # Stats
    st.subheader("📊 Thống kê")
    st.metric("Số tin nhắn", len(st.session_state.messages))
    
    st.divider()
    
    # Help section
    st.subheader("ℹ️ Hướng dẫn")
    st.markdown("""
    - Nhập câu hỏi về sức khỏe tâm thần
    - AI sẽ trả lời dựa trên DSM-5
    - Xem **nguồn tham khảo** dưới mỗi câu trả lời
    - Nhấn **Cuộc trò chuyện mới** để reset
    """)

st.title("🧠 Trợ lý Sức khỏe Tâm thần")

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    msg_type = msg.get("type", "reply")
    text = msg["content"]

    if role == "assistant":
        if msg_type == "warning":
            st.warning(text)
        elif msg_type == "crisis":
            st.error(text)
        else:
            with st.chat_message("assistant"):
                st.markdown(text)
                
                # Display sources if available for this message
                sources_key = f"assistant_{idx}"
                if sources_key in st.session_state.sources_history:
                    sources = st.session_state.sources_history[sources_key]
                    if sources:
                        with st.expander(f"📚 Nguồn tham khảo ({len(sources)} nguồn)"):
                            for i, source in enumerate(sources, 1):
                                score = source.get("score", 0)
                                score_pct = f"{score * 100:.1f}%" if score else "N/A"
                                st.markdown(f"**[{i}]** (Độ liên quan: {score_pct})")
                                st.caption(source.get("text", "")[:300] + "...")
                                st.divider()
    else:
        st.chat_message("user").markdown(text)

user_input = st.chat_input("Nhập tin nhắn...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    st.chat_message("user").markdown(user_input)

    # Call API with session_id
    try:
        payload = {"message": user_input}
        if st.session_state.session_id:
            payload["session_id"] = st.session_state.session_id
            
        with st.spinner("Đang xử lý..."):
            response = requests.post(API_URL, json=payload, timeout=60)
            data = response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout. Vui lòng thử lại.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Không nhận được phản hồi từ server: {e}")
        st.stop()

    if "messages" not in data:
        st.error("Phản hồi không hợp lệ từ server.")
        st.write(data)
        st.stop()

    # Update session_id from response
    if "session_id" in data and data["session_id"]:
        st.session_state.session_id = data["session_id"]

    # Get sources from response
    sources = data.get("sources", [])

    # Process response messages
    for m in data["messages"]:
        msg_type = m.get("type", "reply")
        text = m.get("text", "")

        # Calculate index for this message
        msg_idx = len(st.session_state.messages)
        
        # Store message
        st.session_state.messages.append({
            "role": "assistant",
            "type": msg_type,
            "content": text
        })

        # Store sources for this message (only for reply type)
        if msg_type == "reply" and sources:
            st.session_state.sources_history[f"assistant_{msg_idx}"] = sources

        # Display message
        if msg_type == "warning":
            st.warning(text)
        elif msg_type == "crisis":
            st.error(text)
        else:
            with st.chat_message("assistant"):
                st.markdown(text)
                
                # Display sources
                if sources:
                    with st.expander(f"📚 Nguồn tham khảo ({len(sources)} nguồn)"):
                        for i, source in enumerate(sources, 1):
                            score = source.get("score", 0)
                            score_pct = f"{score * 100:.1f}%" if score else "N/A"
                            st.markdown(f"**[{i}]** (Độ liên quan: {score_pct})")
                            st.caption(source.get("text", "")[:300] + "...")
                            st.divider()