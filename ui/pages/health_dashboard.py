import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_LIST_URL = "http://127.0.0.1:8000/assessment/phq9/list"
API_DETAIL_URL = "http://127.0.0.1:8000/assessment/phq9/details/"

def fetch_assessment_list():
    """Fetch list of PHQ-9 assessment metadata from API."""
    try:
        res = requests.get(API_LIST_URL)
        return res.json().get("items", [])
    except Exception as e:
        print("Failed to load PHQ-9 list:", e)
        return []

def fetch_assessment_detail(filename: str):
    """Fetch full PHQ-9 assessment data by filename."""
    try:
        res = requests.get(API_DETAIL_URL + filename)
        return res.json()
    except Exception as e:
        print("Failed to load PHQ-9 detail:", e)
        return None

st.set_page_config(
    page_title="Bảng theo dõi sức khỏe",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Bảng Theo Dõi Sức Khỏe Tâm Thần (PHQ-9)")

# Load metadata
items = fetch_assessment_list()

if not items:
    st.info("Chưa có dữ liệu PHQ-9 nào. Hãy làm bài đánh giá đầu tiên trong mục PHQ-9.")
else:
    df = pd.DataFrame(items)

    st.subheader("📈 Biểu đồ điểm PHQ-9 theo thời gian")

    df_sorted = df.sort_values(by="timestamp")
    df_sorted["timestamp"] = pd.to_datetime(df_sorted["timestamp"], format="%d/%m/%Y - %H:%M:%S")

    # Sử dụng Plotly để tự động điều chỉnh theo số lượng điểm
    fig = px.line(
        df_sorted,
        x="timestamp",
        y="total_score",
        markers=True,
        labels={"timestamp": "Thời gian", "total_score": "Điểm PHQ-9"}
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(
            tickangle=-45,
            automargin=True
        ),
        yaxis=dict(
            range=[0, 27],  # PHQ-9 có điểm tối đa là 27
            automargin=True
        ),
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    st.plotly_chart(fig, width='stretch')

    st.subheader("📋 Danh sách các bài PHQ-9 đã thực hiện")
    st.dataframe(df, width='stretch')

    st.subheader("🔍 Xem chi tiết bài PHQ-9")

    selected_filename = st.selectbox(
        "Chọn bài kiểm tra để xem chi tiết:",
        options=df["filename"].tolist()
    )

    if selected_filename:
        detail = fetch_assessment_detail(selected_filename)

        if detail:
            st.markdown(f"### ⏱ Thời gian: {detail.get('timestamp')}")
            st.markdown(f"### 🔢 Tổng điểm: **{detail.get('total_score')}**")
            st.markdown(f"### 🟦 Mức độ: **{detail.get('level')}**")
            st.markdown(f"### ⚠️ Nguy cơ tự hại (câu 9): **{detail.get('suicide_risk')}**")