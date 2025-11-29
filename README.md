# 🧠 MindCare - Trợ lý Sức khỏe Tâm thần AI

MindCare là một ứng dụng trợ lý AI hỗ trợ sức khỏe tâm thần, sử dụng công nghệ RAG (Retrieval-Augmented Generation) để cung cấp thông tin dựa trên tiêu chuẩn chẩn đoán DSM-5. Hệ thống giúp người dùng hiểu rõ hơn về các triệu chứng tâm lý và cung cấp hướng dẫn an toàn, đồng thời có chức năng đánh giá sức khỏe tâm thần qua bảng câu hỏi PHQ-9.

## ✨ Tính năng chính

- **💬 Chatbot Tâm lý**: Giao tiếp với AI agent được huấn luyện về sức khỏe tâm thần, sử dụng tri thức từ DSM-5
- **📝 Đánh giá PHQ-9**: Công cụ đánh giá mức độ trầm cảm theo thang điểm chuẩn quốc tế
- **📊 Bảng theo dõi Sức khỏe**: Theo dõi và trực quan hóa kết quả đánh giá theo thời gian
- **🔒 Phát hiện Nguy cơ**: Hệ thống cảnh báo và khuyến nghị khi phát hiện dấu hiệu nguy hiểm
- **🎯 RAG với Vector Database**: Truy vấn thông tin chính xác từ cơ sở tri thức y tế

## 🏗️ Kiến trúc hệ thống

```
MindCare/
├── .env                            # Biến môi trường (API keys)
├── .gitignore                      # Git ignore config
├── requirements.txt                # Python dependencies
├── README.md                       # Tài liệu dự án
├── venv/                           # Virtual environment
├── run_ingest.py                   # Script chạy ingestion pipeline
│ 
├── api/                            # FastAPI backend
│   ├── main.py                     # Entry point API
│   ├── chat.py                     # Chat endpoint
│   ├── agent.py                    # Agent handler
│   └── assessments.py              # PHQ-9 assessment API
│
├── rag/                            # RAG pipeline & AI agent
│   ├── __init__.py
│   ├── agent_core.py               # AI agent chính
│   ├── agent_tools.py              # Tools cho agent (DSM5Query)
│   ├── assessments.py              # Logic đánh giá PHQ-9
│   ├── citation_engine.py          # Query engine với trích dẫn nguồn
│   ├── global_settings.py          # Cấu hình LLM và embedding
│   ├── hybrid_retriever.py         # Hybrid Search (Vector + BM25) & Reranker
│   ├── index_builder.py            # Xây dựng vector index
│   ├── ingest_pipeline.py          # Xử lý và ingest documents
│   ├── memory.py                   # Memory hội thoại theo session
│   └── safety.py                   # Phát hiện nguy cơ
│
├── ui/                             # Streamlit frontend
│   ├── chat.py                     # Giao diện chat chính
│   └── pages/                      # Các trang bổ sung
│       ├── phq9.py                 # Trang đánh giá PHQ-9
│       └── health_dashboard.py     # Dashboard theo dõi
│
└── data/                           # Lưu trữ dữ liệu
    ├── assessments/                # Kết quả PHQ-9 (JSON)
    ├── cache/                      # Cache pipeline
    ├── chroma/                     # ChromaDB vector store
    ├── ingestion_storage/          # Documents đã xử lý
    └── nodes/                      # Serialized nodes cho BM25
```

## 🚀 Cài đặt và Chạy

### Yêu cầu hệ thống

- Python 3.13
- pip hoặc conda

### Các bước cài đặt

1. **Clone repository**
```bash
git clone https://github.com/dodaonam/MindCare.git
cd MindCare
```

2. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

3. **Cấu hình môi trường**

Tạo file `.env` và thêm các thông tin cần thiết:
```
GROQ_API_KEY=your_groq_api_key_here
```

4. **Khởi động Backend API**
```bash
uvicorn api.main:app --reload
```

API sẽ chạy tại: `http://127.0.0.1:8000`

5. **Khởi động Frontend UI**

Mở terminal mới và chạy:
```bash
streamlit run ui/chat.py
```

Giao diện sẽ mở tại: `http://localhost:8501`

## 📖 Sử dụng

### Chat với AI
- Truy cập trang chủ và bắt đầu trò chuyện với trợ lý AI
- Mô tả triệu chứng hoặc thắc mắc về sức khỏe tâm thần
- AI sẽ tham khảo kiến thức DSM-5 để cung cấp thông tin chính xác

### Đánh giá PHQ-9
- Vào trang "PHQ-9" từ sidebar
- Trả lời 9 câu hỏi về tâm trạng trong 2 tuần gần đây
- Xem kết quả đánh giá và khuyến nghị

### Theo dõi Sức khỏe
- Vào trang "Health Dashboard" để xem biểu đồ theo dõi
- Phân tích xu hướng sức khỏe tâm thần theo thời gian

## 🛠️ Công nghệ sử dụng

- **LlamaIndex**: Framework RAG và AI agent
- **ChromaDB**: Vector database
- **FastAPI**: Backend REST API
- **Streamlit**: Frontend UI
- **Groq**: LLM inference
- **HuggingFace**: Embedding models

## ⚠️ Lưu ý quan trọng

- **Không thay thế chẩn đoán y khoa**: Ứng dụng chỉ mang tính chất hỗ trợ và tham khảo
- **Không dùng cho cấp cứu**: Nếu có ý định tự hại, vui lòng liên hệ ngay với cơ sở y tế hoặc đường dây nóng tâm lý
- **Bảo mật dữ liệu**: Dữ liệu cá nhân được lưu trữ local, không gửi lên server bên thứ ba

## 📝 License

Dự án này được phát triển cho mục đích nghiên cứu và giáo dục.