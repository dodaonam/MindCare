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

# Initialize session state for form reset
if "phq9_submitted" not in st.session_state:
    st.session_state.phq9_submitted = False
if "phq9_result" not in st.session_state:
    st.session_state.phq9_result = None

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
    # Use default value 0, reset after submission
    default_val = 0
    score = st.radio(
        label=q,
        options=[0, 1, 2, 3],
        index=default_val,
        key=f"phq9_q{idx}_{st.session_state.get('phq9_form_key', 0)}",
        horizontal=True
    )
    scores.append(score)

st.divider()

# Show previous result if exists
if st.session_state.phq9_result:
    result = st.session_state.phq9_result
    st.success("🎉 Kết quả đánh giá gần nhất:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔢 Tổng điểm", result.get('total_score'))
    with col2:
        st.metric("🟦 Mức độ", result.get('level'))
    with col3:
        st.metric("⚠️ Nguy cơ tự hại", result.get('suicide_risk'))
    
    saved_file = result.get("saved_file")
    if saved_file:
        st.caption(f"📁 File: `{saved_file}`")
    
    st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📤 Gửi bài đánh giá", use_container_width=True):
        if len(scores) != 9:
            st.error("Vui lòng trả lời đầy đủ 9 câu hỏi.")
            st.stop()

        result = submit_answers(scores)

        if not result:
            st.error("Không gửi được bài đánh giá. Vui lòng thử lại.")
        elif result.get("error"):
            st.error(result["error"])
        else:
            # Store result and reset form
            st.session_state.phq9_result = result
            st.session_state.phq9_form_key = st.session_state.get('phq9_form_key', 0) + 1
            st.rerun()

with col2:
    if st.button("🔄 Làm lại", use_container_width=True):
        st.session_state.phq9_result = None
        st.session_state.phq9_form_key = st.session_state.get('phq9_form_key', 0) + 1
        st.rerun()
