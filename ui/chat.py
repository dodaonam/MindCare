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
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input("Nhập tin nhắn...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    st.chat_message("user").markdown(user_input)

    try:
        response = requests.post(API_URL, json={"message": user_input})
        bot_reply = response.json().get("reply", "Không nhận được phản hồi từ server.")
    except Exception as e:
        bot_reply = f"Lỗi kết nối đến API: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
    st.chat_message("assistant").markdown(bot_reply)