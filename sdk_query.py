"""Search + generation over the SDK reference index, with:
  - a strategy switch ("baseline" vs "structured") so the same query can be
    run against either chunking strategy,
  - an optional sdk_version metadata filter,
  - forced citations (chunk_id) per claim, and
  - a forced refusal path for out-of-corpus questions (the prompt gives the
    model no discretion to "use its best judgement").
"""

import os
import pickle
import re

import faiss
import numpy as np
import requests

import config
from pdf_reader import get_embedding_model

SDK_INDEX_DIR = "sdk_index"

_cache = {}


def load_strategy(strategy_name):
    if strategy_name in _cache:
        return _cache[strategy_name]

    index_path = os.path.join(SDK_INDEX_DIR, f"{strategy_name}.index")
    chunks_path = os.path.join(SDK_INDEX_DIR, f"{strategy_name}.pkl")

    if not os.path.exists(index_path):
        raise RuntimeError(
            f"'{index_path}' not found. Run 'python sdk_ingest.py' first."
        )

    index = faiss.read_index(index_path)
    with open(chunks_path, "rb") as f:
        data = pickle.load(f)

    _cache[strategy_name] = (index, data["chunks"], data["metadata"])
    return _cache[strategy_name]


def query_to_vector(query):
    vector = get_embedding_model().encode([query], convert_to_numpy=True)
    vector = np.array(vector, dtype="float32")
    faiss.normalize_L2(vector)
    return vector


def search_sdk(query, strategy_name, top_k=5, sdk_version=None):
    """Search one strategy's index. If sdk_version is given, filter to only
    chunks whose metadata sdk_version matches, THEN take top_k — the filter
    is applied over the full ranked list, not just the first top_k
    unfiltered hits, so it can genuinely change which chunk lands at rank 1."""

    index, chunks, metadata = load_strategy(strategy_name)

    query_vector = query_to_vector(query)

    # Over-fetch the entire index (it's small) so filtering afterwards still
    # sees the full ranking rather than an already-truncated top_k.
    n_total = index.ntotal
    distances, indices = index.search(query_vector, n_total)

    results = []
    for idx, score in zip(indices[0], distances[0]):
        if idx == -1:
            continue

        meta = metadata[idx]

        if sdk_version is not None and meta["sdk_version"] != sdk_version:
            continue

        results.append({
            "rank": len(results) + 1,
            "chunk_id": meta["chunk_id"],
            "chunk": chunks[idx],
            "metadata": meta,
            "score": float(score),
        })

        if len(results) >= top_k:
            break

    return results


def hit_in_top_5(results, expected_page_id):
    return any(r["metadata"]["page_id"] == expected_page_id for r in results[:5])


GROUNDED_PROMPT_TEMPLATE = """You are a documentation assistant. You must answer ONLY from the
CONTEXT chunks below. Each chunk is labeled with its chunk_id.

Rules (follow exactly, no exceptions):
1. Every sentence of your answer MUST end with a citation in the form
   [chunk_id], copied exactly from the label of the chunk it came from.
   This applies even when the sentence introduces or describes a code
   sample copied from that chunk — the code fence itself does not need
   a citation, but the sentence pointing to it does.
2. If the CONTEXT does not contain the answer, you MUST respond with
   exactly this sentence and nothing else:
   "I cannot answer this from the indexed SDK reference pages."
3. Do not use outside knowledge. Do not guess. Do not fill gaps with
   plausible-sounding values. There is no acceptable case where you
   invent a parameter name, default, or number that is not in CONTEXT.

Example of correctly cited output:
"The default is 500ms [structured:v3-client-send:1]. It is passed as a
keyword argument to send() [structured:v3-client-send:3]."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""


def build_context(results):
    parts = []
    for r in results:
        m = r["metadata"]
        anchor = f"{m['source_file']}#{m['section']}"
        parts.append(
            f"[{r['chunk_id']}] (page={m['source_file']}, anchor=\"{anchor}\", "
            f"sdk_version={m['sdk_version']}, page_type={m['page_type']})\n{r['chunk']}"
        )
    return "\n\n---\n\n".join(parts)


def generate_answer(query, results, model=None):
    model = model or config.OLLAMA_MODEL

    if not results:
        return "I cannot answer this from the indexed SDK reference pages."

    context = build_context(results)
    prompt = GROUNDED_PROMPT_TEMPLATE.format(context=context, query=query)

    try:
        response = requests.post(
            config.OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    except requests.exceptions.ConnectionError:
        return "Could not connect to Ollama. Make sure Ollama is installed and running."
    except requests.exceptions.RequestException as e:
        return f"Ollama request failed: {e}"


CITATION_RE = re.compile(r"\[([a-zA-Z0-9_.:\-]+)\]")


def extract_citations(answer_text):
    return CITATION_RE.findall(answer_text)


def citations_resolve(answer_text, results):
    """Return (all_resolve: bool, unresolved: list[str]) — every [chunk_id]
    found in the answer must match a chunk_id actually present in the
    retrieved results passed to the model."""

    valid_ids = {r["chunk_id"] for r in results}
    found = extract_citations(answer_text)
    unresolved = [c for c in found if c not in valid_ids]
    return (len(unresolved) == 0 and len(found) > 0), unresolved
