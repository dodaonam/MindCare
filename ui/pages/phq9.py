import streamlit as st
import requests

API_QUESTION_URL = "http://127.0.0.1:8000/assessment/phq9/questions"
API_SCORE_URL = "http://127.0.0.1:8000/assessment/phq9/score"

def fetch_questions():
    """Fetch PHQ-9 questions from backend API."""
    try:
        res = requests.get(API_QUESTION_URL)
        return res.json()
    except Exception as e:
        print("Failed to load PHQ-9 questions:", e)
        return None

def submit_answers(scores: list[int]):
    """Submit PHQ-9 answers to API and return result."""
    try:
        res = requests.post(API_SCORE_URL, json={"scores": scores})
        return res.json()
    except Exception as e:
        print("Failed to submit PHQ-9 answers:", e)
        return None

st.set_page_config(
    page_title="Đánh giá PHQ-9",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Bài Đánh Giá PHQ-9")
st.markdown("Công cụ đánh giá mức độ trầm cảm trong 2 tuần gần đây.")

# Load question list
data = fetch_questions()
if data is None:
    st.error("Không tải được câu hỏi từ API.")
    st.stop()

questions = data.get("questions", [])
scale_desc = data.get("scale", "")

st.subheader("📌 Hướng dẫn")
st.info(f"Thang điểm: **{scale_desc}**")

scores = []

st.subheader("📋 Câu hỏi")
for idx, q in enumerate(questions):
    score = st.radio(
        label=q,
        options=[0, 1, 2, 3],
        key=f"phq9_q{idx}",
        horizontal=True
    )
    scores.append(score)

st.divider()

if st.button("📤 Gửi bài đánh giá"):
    if len(scores) != 9:
        st.error("Vui lòng trả lời đầy đủ 9 câu hỏi.")
        st.stop()

    result = submit_answers(scores)

    if not result:
        st.error("Không gửi được bài đánh giá. Vui lòng thử lại.")
    elif result.get("error"):
        st.error(result["error"])
    else:
        st.success("🎉 Đã chấm điểm thành công!")

        st.markdown(f"### 🔢 Tổng điểm: **{result.get('total_score')}**")
        st.markdown(f"### 🟦 Mức độ: **{result.get('level')}**")
        st.markdown(f"### ⚠️ Nguy cơ tự hại (câu 9): **{result.get('suicide_risk')}**")

        saved_file = result.get("saved_file")
        if saved_file:
            st.markdown(f"📁 Dữ liệu đã được lưu vào file:\n`{saved_file}`")
