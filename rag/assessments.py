import json
import os
from datetime import datetime
from rag.global_settings import ASSESSMENT_DIR

def save_phq9_result(result: dict) -> str:
    os.makedirs(ASSESSMENT_DIR, exist_ok=True)

    file_ts = datetime.now().strftime("%d%m%Y-%H%M%S")

    filename = f"phq9-{file_ts}.json"
    filepath = os.path.join(ASSESSMENT_DIR, filename)

    result["timestamp"] = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return filepath

def list_assessments() -> list:
    if not os.path.exists(ASSESSMENT_DIR):
        return []

    files = [
        f for f in os.listdir(ASSESSMENT_DIR)
        if f.startswith("phq9-") and f.endswith(".json")
    ]

    return sorted(files, reverse=True)

def load_assessment(filename: str) -> dict:
    filepath = os.path.join(ASSESSMENT_DIR, filename)

    if not os.path.isfile(filepath):
        return {"error": "File not found"}

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)