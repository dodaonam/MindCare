from fastapi import APIRouter
from pydantic import BaseModel
from rag.assessments import (
    save_phq9_result,
    load_assessment,
    load_all_assessments_metadata
)

router = APIRouter()

PHQ9_QUESTIONS = [
    "1. Có cảm thấy mất hứng thú hoặc không thể thưởng thức những hoạt động thường ngày không?",
    "2. Có cảm thấy buồn rầu, tuyệt vọng hoặc không hy vọng không?",
    "3. Có gặp khó khăn khi ngủ, hoặc ngủ quá nhiều không?",
    "4. Có cảm thấy mệt mỏi hoặc thiếu sức sống không?",
    "5. Có cảm thấy chán ăn hoặc ăn quá nhiều không?",
    "6. Có cảm thấy mình là người thất bại, mất tự tin hoặc cảm giác tội lỗi không?",
    "7. Có gặp khó khăn khi tập trung vào công việc, như đọc sách hoặc xem tivi không?",
    "8. Có cảm thấy bản thân di chuyển hoặc nói chậm lại hoặc ngược lại, bồn chồn khó chịu không?",
    "9. Có suy nghĩ rằng mình sẽ tốt hơn nếu chết hoặc tự làm hại bản thân không?"
]

class PHQ9Answers(BaseModel):
    scores: list[int]

@router.get("/assessment/phq9/questions")
def get_phq9_questions():
    return {
        "questions": PHQ9_QUESTIONS,
        "scale": "0=Không bao giờ, 1=Vài ngày, 2=Hơn nửa số ngày, 3=Gần như mỗi ngày"
    }

@router.post("/assessment/phq9/score")
def score_phq9(data: PHQ9Answers):
    scores = data.scores

    if len(scores) != 9:
        return {"error": "PHQ-9 cần đúng 9 câu trả lời, dạng số 0-3."}

    total = sum(scores)
    q9 = scores[8]

    # PHQ-9 classification
    if total <= 4:
        level = "Không hoặc rất nhẹ"
    elif total <= 9:
        level = "Nhẹ"
    elif total <= 14:
        level = "Trung bình"
    elif total <= 19:
        level = "Nặng"
    else:
        level = "Rất nặng"

    # Suicide risk detection
    if q9 == 0:
        suicide_risk = "không"
    elif q9 == 1:
        suicide_risk = "nhẹ"
    elif q9 == 2:
        suicide_risk = "trung bình"
    else:
        suicide_risk = "nghiêm trọng"

    result = {
        "total_score": total,
        "level": level,
        "suicide_risk": suicide_risk,
        "q9_score": q9,
    }

    saved_path = save_phq9_result(result)

    return {
        "success": True,
        "saved_file": saved_path,
        **result
    }

@router.get("/assessment/phq9/list")
def phq9_list():
    metadata = load_all_assessments_metadata()
    return {
        "count": len(metadata),
        "items": metadata
    }

@router.get("/assessment/phq9/details/{filename}")
def phq9_details(filename: str):
    data = load_assessment(filename)
    return data