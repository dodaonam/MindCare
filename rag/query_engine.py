from llama_index.core import Settings
from llama_index.llms.groq import Groq
from rag.index_builder import get_or_build_index
from rag.global_settings import GROQ_API_KEY

def init_llm():
    Settings.llm = Groq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=GROQ_API_KEY,
        temperature=0.6,
        )

def build_query_engine():
    """Load the existing index and create a Query Engine."""
    init_llm()
    index = get_or_build_index()
    
    query_engine = index.as_query_engine(similarity_top_k=3, response_mode="compact")
    
    print("Query engine initialized successfully.")
    return query_engine

def test_query():
    qe = build_query_engine()
    queries = [
        "Thời gian tồn tại tối thiểu của các triệu chứng Rối loạn lo âu chia tách là bao lâu đối với trẻ em và người lớn?",
        "Để chẩn đoán giai đoạn hưng cảm trong Rối loạn lưỡng cực I, các triệu chứng phải kéo dài tối thiểu bao lâu và cần thỏa mãn bao nhiêu triệu chứng phụ?",
        "Sự khác biệt cơ bản trong mong muốn quan hệ xã hội giữa Rối loạn nhân cách né tránh và Rối loạn nhân cách schizoid (khép kín) là gì?",
        "Những biểu hiện nào được coi là kiểu hành vi thu hẹp, lặp lại, hứng thú, hoặc hoạt động trong chẩn đoán Rối loạn phổ tự kỷ?",
        "Ai là người chỉ đạo và hiệu đính tài liệu 'TIÊU CHUẨN CHẨN ĐOÁN CÁC RỐI LOẠN TÂM THẦN THEO DSM-5' này?",
        "Tài liệu 'TIÊU CHUẨN CHẨN ĐOÁN CÁC RỐI LOẠN TÂM THẦN THEO DSM-5' được phát hành bởi đơn vị nào và với mục đích sử dụng gì?"
    ]

    print("\nStarting DSM-5 query tests...")
    for i, q in enumerate(queries):
        print(f"\n---\nQuestion {i+1}: {q}")
        response = qe.query(q)
        print(f"Answer:\n{response}")

    print("\nAll test queries completed successfully.")

if __name__ == "__main__":
    test_query()