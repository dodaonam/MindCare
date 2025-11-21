import streamlit as st
import requests

st.set_page_config(
    page_title="Mental Health Chat",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Trợ lý Sức khỏe Tâm thần")

API_URL = "http://127.0.0.1:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role = msg["role"]
    msg_type = msg.get("type", "reply")
    text = msg["content"]

    if role == "assistant":
        if msg_type == "warning":
            st.warning(text)
        elif msg_type == "crisis":
            st.error(text)
        else:
            st.chat_message("assistant").markdown(text)
    else:
        st.chat_message("user").markdown(text)

user_input = st.chat_input("Nhập tin nhắn...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    st.chat_message("user").markdown(user_input)

    try:
        response = requests.post(API_URL, json={"message": user_input}, timeout=20)
        data = response.json()
    except Exception as e:
        st.error("Không nhận được phản hồi từ server.")
        st.stop()

    if "messages" not in data:
        st.error("Phản hồi không hợp lệ từ server.")
        st.write(data)
        st.stop()

    for m in data["messages"]:
        msg_type = m.get("type", "reply")
        text = m.get("text", "")

        st.session_state.messages.append({
            "role": "assistant",
            "type": msg_type,
            "content": text
        })

        if msg_type == "warning":
            st.warning(text)
        elif msg_type == "crisis":
            st.error(text)
        else:
            st.chat_message("assistant").markdown(text)