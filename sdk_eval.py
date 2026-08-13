"""Search-only evaluation: run the 8 fixed questions (sdk_docs/questions.json,
written before any retrieval was run) against both chunking strategies and
record hit-in-top-5 per question. Dumps full ranked result lists for both
strategies to sdk_eval_dump.json for the write-up appendix.
"""

import json

import sdk_query as q

QUESTIONS_PATH = "sdk_docs/questions.json"
DUMP_PATH = "sdk_eval_dump.json"


def expected_page_id(known_page):
    # known_page like "v3/client_send.md" -> page_id "v3-client-send"
    version, filename = known_page.split("/")
    stem = filename.replace(".md", "").replace("_", "-")
    return f"{version}-{stem}"


def main():
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    dump = {"baseline": [], "structured": []}
    hit_table = []

    for strategy in ("baseline", "structured"):
        hits = 0
        for item in questions:
            exp_id = expected_page_id(item["known_page"])
            results = q.search_sdk(item["question"], strategy, top_k=5)
            hit = q.hit_in_top_5(results, exp_id)
            hits += int(hit)

            hit_table.append({
                "id": item["id"],
                "strategy": strategy,
                "question": item["question"],
                "expected_page_id": exp_id,
                "hit_top5": hit,
                "top5_page_ids": [r["metadata"]["page_id"] for r in results],
            })

            dump[strategy].append({
                "id": item["id"],
                "question": item["question"],
                "expected_page_id": exp_id,
                "hit_top5": hit,
                "results": [
                    {
                        "rank": r["rank"],
                        "chunk_id": r["chunk_id"],
                        "score": round(r["score"], 4),
                        "page_id": r["metadata"]["page_id"],
                        "sdk_version": r["metadata"]["sdk_version"],
                        "section": r["metadata"]["section"],
                        "text_preview": r["chunk"][:160],
                    }
                    for r in results
                ],
            })

        print(f"{strategy}: {hits}/{len(questions)}")

    with open(DUMP_PATH, "w") as f:
        json.dump(dump, f, indent=2)

    print()
    print(f"{'ID':4} {'Strategy':11} {'Hit':4} Question")
    for row in hit_table:
        print(f"{row['id']:4} {row['strategy']:11} {'YES' if row['hit_top5'] else 'NO':4} {row['question']}")


if __name__ == "__main__":
    main()
