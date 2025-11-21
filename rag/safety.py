import re
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import Settings

CRISIS_KEYWORDS = [
    r"tự\s*hại",
    r"tự\s*tử",
    r"tự\s*sát",
    r"muốn\s*chết",
    r"muốn\s*tự\s*tử",
    r"muốn\s*tự\s*sát",
    r"không\s*muốn\s*sống",
    r"muốn\s*kết\s*liễu",
    r"kết\s*liễu\s*(chính\s*)?mình",
    r"kết\s*thúc\s*mọi\s*thứ",
    r"muốn\s*die\b",

    r"ý\s*định\s*tự\s*(tử|sát)",
    r"suy\s*nghĩ\s*tự\s*(tử|sát)",
    r"nghĩ\s*đến\s*cái\s*chết",
    r"bàn\s*về\s*cái\s*chết",
    r"kế\s*hoạch\s*(tự\s*hại|tự\s*tử|tự\s*sát)",
    r"lên\s*kế\s*hoạch\s*(tự\s*hại|tự\s*tử|tự\s*kết\s*liễu)",
    r"nỗ\s*lực\s*tự\s*(tử|sát)",
    r"cố\s*gắng\s*tự\s*(tử|sát)",
    r"đe\s*dọa\s*tự\s*(tử|sát)",
    r"đe\s*dọa\s*sẽ\s*tự\s*(tử|sát)",
    r"hành\s*vi\s*tự\s*(tử|sát)",
    r"tự\s*giết\s*mình",
    r"tự\s*giết\s*chết\s*bản\s*thân",
    r"tự\s*làm\s*mình\s*chết",

    r"nhảy\s*lầu",
    r"nhảy\s*sông",
    r"treo\s*cổ",
    r"cắt\s*cổ\s*tay",
    r"tự\s*cắt\s*tay",
    r"rạch\s*tay",
    r"rạch\s*cổ\s*tay",
    r"uống\s*thuốc\s*độc",
    r"uống\s*thật\s*nhiều\s*thuốc",
    r"đập\s*đầu",
    r"cắn\s*lưỡi",
    r"đốt\s*mình",

    r"muốn\s*ngủ\s*một\s*giấc\s*không\s*bao\s*giờ\s*tỉnh",
    r"ước\s*gì\s*mình\s*biến\s*mất\s*vĩnh\s*viễn",
]

WARNING_KEYWORDS = [
    r"tuyệt\s*vọng",
    r"stress",
    r"hoảng\s*sợ",
    r"hoảng\s*loạn",
    r"lo\s*lắng",
    r"lo\s*âu",
    r"khó\s*thở",
    r"mệt\s*mỏi\s*quá",
    r"chán\s*nản",
    r"cảm\s*thấy\s*tuyệt\s*vọng",
    r"cuộc\s*sống\s*không\s*còn\s*ý\s*nghĩa",
    r"tôi\s*là\s*gánh\s*nặng",
    r"không\s*chịu\s*nổi\s*đau\s*đớn",
    r"muốn\s*biến\s*mất",
    r"muốn\s*biến\s*mất\s*khỏi\s*đây",
    r"cảm\s*thấy\s*cô\s*lập",
    r"xa\s*lánh\s*mọi\s*người",
    r"buồn\s*bã\s*kéo\s*dài",
    r"chán\s*nản\s*mọi\s*thứ",
    r"mất\s*hứng\s*thú\s*với\s*cuộc\s*sống",
    r"mất\s*đi\s*sự\s*thích\s*thú\s*với\s*xung\s*quanh",
    r"không\s*chăm\s*sóc\s*bản\s*thân",
    r"bế\s*tắc\s*cuộc\s*sống",
    r"mất\s*phương\s*hướng",
    r"đau\s*khổ\s*tột\s*độ",
    r"trầm\s*uất",
    r"trầm\s*cảm",
    r"chấn\s*thương",
    r"khủng\s*hoảng",
    r"ý\s*nghĩ\s*tiêu\s*cực\s*kéo\s*dài",
    r"cảm\s*thấy\s*ích\s*kỷ\s*nếu\s*sống\s*tiếp",
    r"khó\s*khăn\s*đưa\s*ra\s*quyết\s*định",
    r"thay\s*đổi\s*thói\s*quen",
    r"cảm\s*xúc\s*trống\s*rỗng",
    r"thu\s*mình",
    r"đột\s*nhiên\s*bình\s*tĩnh",

    r"hành\s*vi\s*khác\s*thường",
    r"nói\s*năng\s*lộn\s*xộn",
    r"khó\s*hiểu",
    r"mơ\s*hồ",
    r"rối\s*loạn\s*cảm\s*xúc",
    r"rối\s*loạn\s*tâm\s*thần",

    r"nghe\s*thấy\s*tiếng\s*nói\s*xui\s*khiến",
    r"nghe\s*thấy\s*tiếng\s*nói\s*lạ",
    r"có\s*người\s*theo\s*dõi",
    r"bị\s*đầu\s*độc",
    r"hoang\s*tưởng",
    r"ảo\s*giác",
    r"ma\s*quỷ\s*xui\s*khiến",
    r"nghĩ\s*có\s*chip\s*trong\s*đầu",
]

CRISIS_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CRISIS_KEYWORDS]
WARNING_PATTERNS = [re.compile(p, re.IGNORECASE) for p in WARNING_KEYWORDS]

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def keyword_match(text: str) -> dict:
    """Detect potential crisis/warning keywords in the message."""
    text_norm = normalize_text(text)

    crisis_hits = [pat.pattern for pat in CRISIS_PATTERNS if pat.search(text_norm)]
    warning_hits = [pat.pattern for pat in WARNING_PATTERNS if pat.search(text_norm)]

    return {
        "crisis_hits": crisis_hits,
        "warning_hits": warning_hits,
    }

SAFETY_PROMPT = """
You are a mental health safety classifier. The user's message is in Vietnamese.

Classify the message into one of the three categories below:

1. CRISIS — The user expresses intent, plan, or immediate risk of self-harm or suicide.

2. WARNING — The user expresses significant emotional distress such as prolonged sadness, persistent hopelessness, long-term depressive symptoms, or repeated negative feelings. 
IMPORTANT: Mild or single neutral statements like "tôi buồn", "tôi chán nản", "tôi thấy mệt" should NOT be classified as WARNING unless they clearly indicate ongoing or severe emotional difficulty.

3. SAFE — The user is asking questions, expressing light or temporary emotions, or discussing mental health academically.

Return ONLY: CRISIS, WARNING, or SAFE.
"""

def llm_classify(text: str) -> str:
    """Use LLM to classify message contextually."""
    llm = Settings.llm

    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=SAFETY_PROMPT),
        ChatMessage(role=MessageRole.USER, content=text),
    ]

    res = llm.chat(messages)
    raw = res.message.content.strip().upper()

    label = re.sub(r"[^A-Z]", "", raw)

    if label in ["CRISIS", "WARNING", "SAFE"]:
        return label
    return "SAFE"

def safety_check(text: str) -> dict:
    """Hybrid safety detection: keyword scan → LLM contextual classification."""
    scan = keyword_match(text)

    # No risky keywords → SAFE immediately
    if not scan["crisis_hits"] and not scan["warning_hits"]:
        return {
            "level": "safe",
            "source": "keyword",
            "crisis_matches": [],
            "warning_matches": [],
        }

    # Keywords detected → LLM decides final severity
    llm_result = llm_classify(text).lower()

    return {
        "level": llm_result,
        "source": "llm",
        "crisis_matches": scan["crisis_hits"],
        "warning_matches": scan["warning_hits"],
    }