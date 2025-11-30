import streamlit as st
import requests
import json

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

    # Prepare payload
    payload = {"message": user_input}
    if st.session_state.session_id:
        payload["session_id"] = st.session_state.session_id

    # Use streaming API
    try:
        with requests.post(API_URL, json=payload, stream=True, timeout=120) as response:
            full_response = ""
            sources = []
            warning_shown = False
            crisis_shown = False
            
            # Create placeholder for streaming response
            response_placeholder = None
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        try:
                            event_data = json.loads(line_text[6:])
                            event_type = event_data.get('type')
                            data = event_data.get('data')
                            
                            if event_type == 'safety':
                                # Safety check received
                                pass
                            
                            elif event_type == 'warning' and not warning_shown:
                                st.warning(data)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "type": "warning",
                                    "content": data
                                })
                                warning_shown = True
                            
                            elif event_type == 'crisis' and not crisis_shown:
                                st.error(data)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "type": "crisis",
                                    "content": data
                                })
                                crisis_shown = True
                            
                            elif event_type == 'token':
                                if response_placeholder is None:
                                    response_placeholder = st.chat_message("assistant").empty()
                                full_response += data
                                response_placeholder.markdown(full_response + "▌")
                            
                            elif event_type == 'sources':
                                sources = data if data else []
                            
                            elif event_type == 'done':
                                if event_data.get('session_id'):
                                    st.session_state.session_id = event_data['session_id']
                            
                            elif event_type == 'error':
                                st.error(f"❌ Error: {data}")
                                
                        except json.JSONDecodeError:
                            pass
            
            # Finalize response
            if full_response and response_placeholder:
                response_placeholder.markdown(full_response)
                
                # Calculate message index
                msg_idx = len(st.session_state.messages)
                
                # Store message
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "reply",
                    "content": full_response
                })
                
                # Store sources
                if sources:
                    st.session_state.sources_history[f"assistant_{msg_idx}"] = sources
                    
                    # Display sources
                    with st.expander(f"📚 Nguồn tham khảo ({len(sources)} nguồn)"):
                        for i, source in enumerate(sources, 1):
                            score = source.get("score", 0)
                            score_pct = f"{score * 100:.1f}%" if score else "N/A"
                            st.markdown(f"**[{i}]** (Độ liên quan: {score_pct})")
                            st.caption(source.get("text", "")[:300] + "...")
                            st.divider()
                            
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout. Vui lòng thử lại.")
    except Exception as e:
        st.error(f"❌ Lỗi kết nối: {e}")