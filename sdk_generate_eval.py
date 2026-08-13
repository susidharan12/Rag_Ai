"""Run the 3 answerable + 3 out-of-corpus questions through real generation
(Ollama) against the structured-strategy index, and dump verbatim
transcripts + citation-resolution checks to sdk_generation_dump.json.
"""

import json

import sdk_query as q

STRATEGY = "structured"
ANSWERABLE_IDS = ["Q1", "Q5", "Q8"]


def run_answerable():
    with open("sdk_docs/questions.json") as f:
        questions = {item["id"]: item for item in json.load(f)}

    out = []
    for qid in ANSWERABLE_IDS:
        item = questions[qid]
        results = q.search_sdk(item["question"], STRATEGY, top_k=5, sdk_version="v3")
        answer = q.generate_answer(item["question"], results)
        resolves, unresolved = q.citations_resolve(answer, results)

        out.append({
            "id": qid,
            "question": item["question"],
            "known_page": item["known_page"],
            "known_answer": item["known_answer"],
            "retrieved_chunk_ids": [r["chunk_id"] for r in results],
            "answer": answer,
            "citations_resolve": resolves,
            "unresolved_citations": unresolved,
        })
        print(f"[{qid}] {item['question']}")
        print(f"  answer: {answer}")
        print(f"  citations resolve: {resolves} (unresolved={unresolved})")
        print()

    return out


def run_refusals():
    with open("sdk_docs/oos_questions.json") as f:
        oos = json.load(f)

    out = []
    for item in oos:
        results = q.search_sdk(item["question"], STRATEGY, top_k=5, sdk_version="v3")
        answer = q.generate_answer(item["question"], results)
        refused = answer.strip() == "I cannot answer this from the indexed SDK reference pages."

        out.append({
            "id": item["id"],
            "question": item["question"],
            "why_unanswerable": item["why_unanswerable"],
            "retrieved_chunk_ids": [r["chunk_id"] for r in results],
            "answer": answer,
            "refused": refused,
        })
        print(f"[{item['id']}] {item['question']}")
        print(f"  answer: {answer}")
        print(f"  refused correctly: {refused}")
        print()

    return out


def main():
    print("=== Answerable questions (with citations) ===\n")
    answerable = run_answerable()

    print("=== Out-of-corpus questions (must refuse) ===\n")
    refusals = run_refusals()

    with open("sdk_generation_dump.json", "w") as f:
        json.dump({"answerable": answerable, "refusals": refusals}, f, indent=2)


if __name__ == "__main__":
    main()
