"""Interactive REPL for the SDK reference index — same idea as query.py,
pointed at sdk_index/ instead of vectors.index.

Usage:
  python sdk_ask.py                          # structured strategy, no version filter
  python sdk_ask.py --strategy baseline      # use the baseline chunker's index
  python sdk_ask.py --sdk-version v3         # only retrieve from v3 pages
"""

import argparse

import sdk_query as q


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=["baseline", "structured"], default="structured")
    parser.add_argument("--sdk-version", choices=["v2", "v3"], default=None)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    print(f"Strategy: {args.strategy} | sdk_version filter: {args.sdk_version or 'none'}")

    try:
        q.load_strategy(args.strategy)
    except RuntimeError as e:
        print(f"\n{e}")
        return

    while True:
        query = input("\nEnter your question (or type 'exit'): ")

        if query.lower().strip() == "exit":
            print("Goodbye!")
            break

        if not query.strip():
            print("Please enter a question.")
            continue

        results = q.search_sdk(query, args.strategy, top_k=args.top_k, sdk_version=args.sdk_version)

        print("\nRetrieved:")
        for r in results:
            print(f"  [{r['rank']}] {r['chunk_id']}  score={r['score']:.4f}  ({r['metadata']['section']})")

        answer = q.generate_answer(query, results)
        print(f"\n{answer}")


if __name__ == "__main__":
    main()
