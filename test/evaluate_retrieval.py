import json
from rag.query_engine import build_query_engine
from rag.global_settings import DATASET_PATH,OUTPUT_FILE

def evaluate():
    print("Loading Query Engine...")
    qe = build_query_engine()

    print(f"Loading dataset: {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    print(f"Total questions: {total}")
    print(f"Saving results to {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        out.write("=== EVALUATION RESULTS ===\n\n")
        out.write(f"Total questions: {total}\n\n")

        for i, item in enumerate(dataset):
            question = item["question"]
            reference = item["reference"]

            out.write("\n------------------------------------\n")
            out.write(f"QUESTION {i+1}: {question}\n")
            out.write(f"REFERENCE: {reference}\n")

            # Model answer
            answer = qe.query(question)
            out.write(f"\nANSWER:\n{answer}\n")

            # Retrieved chunks
            out.write("\nRETRIEVED CONTEXTS:\n")
            nodes = qe.retrieve(question)

            for idx, n in enumerate(nodes):
                out.write(f"\n  ---- Node {idx+1} (Score: {n.score:.3f}) ----\n")
                out.write(n.get_content().strip()[:500] + "\n")

            out.write("\n------------------------------------\n")

        out.write("\n=== DONE — Review manually to verify correctness ===\n")

    print(f"\nEvaluation complete. Please check: {OUTPUT_FILE}")

if __name__ == "__main__":
    evaluate()