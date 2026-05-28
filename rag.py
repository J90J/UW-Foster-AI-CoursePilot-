from __future__ import annotations

import math
from dataclasses import dataclass

from openai import OpenAI

from config import OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL, TOP_K
from db import connect, decode_vector


SUBJECT_KEYWORDS = {
    "FIN": ["finance", "financial", "valuation", "investment", "investing", "portfolio", "corporate finance"],
    "MKTG": ["marketing", "consumer", "pricing", "brand", "sales"],
    "ENTRE": ["entrepreneurship", "startup", "venture", "founder", "innovation"],
    "ACCT": ["accounting", "accountant", "financial statement", "tax"],
    "OPMGT": ["operations", "supply chain", "process", "sustainable design"],
    "MGMT": ["management", "leadership", "strategy", "culture", "negotiation"],
    "IBUS": ["international", "global business"],
    "QMETH": ["quantitative", "statistics", "data", "analytics"],
}


SYSTEM_PROMPT = """You are a UW Foster MBA course planning assistant.
Answer only from the provided course materials. Help students understand course content,
assignments, grading, schedules, and elective fit for goals such as finance, consulting,
marketing, entrepreneurship, operations, sustainability, product management, and leadership.
When recommending courses, explain the rationale and mention relevant tradeoffs.
If the retrieved materials do not contain enough information, say what is missing.
Always cite sources using bracketed citation ids like [1] or [2]."""


@dataclass
class RetrievedChunk:
    id: int
    title: str
    filename: str
    page_start: int | None
    page_end: int | None
    text: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def embed_query(client: OpenAI, query: str) -> list[float]:
    response = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=query)
    return response.data[0].embedding


def metadata_boost(query: str, title: str, filename: str) -> float:
    query_lower = query.lower()
    metadata = f"{title} {filename}".lower()
    boost = 0.0

    for subject, keywords in SUBJECT_KEYWORDS.items():
        subject_lower = subject.lower()
        if subject_lower in metadata and any(keyword in query_lower for keyword in keywords):
            boost += 0.09

    for token in query_lower.replace("/", " ").replace("-", " ").split():
        if len(token) >= 4 and token in metadata:
            boost += 0.015

    return min(boost, 0.14)


def retrieve(client: OpenAI, query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    query_embedding = embed_query(client, query)
    conn = connect()
    rows = conn.execute(
        """
        SELECT
            chunks.id,
            chunks.text,
            chunks.page_start,
            chunks.page_end,
            chunks.embedding_json,
            documents.title,
            documents.filename
        FROM chunks
        JOIN documents ON documents.id = chunks.document_id
        """
    ).fetchall()
    conn.close()

    scored: list[RetrievedChunk] = []
    for row in rows:
        semantic_score = cosine_similarity(query_embedding, decode_vector(row["embedding_json"]))
        score = semantic_score + metadata_boost(query, row["title"], row["filename"])
        scored.append(
            RetrievedChunk(
                id=row["id"],
                title=row["title"],
                filename=row["filename"],
                page_start=row["page_start"],
                page_end=row["page_end"],
                text=row["text"],
                score=score,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]


def format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        page_label = ""
        if chunk.page_start and chunk.page_end:
            page_label = f", pages {chunk.page_start}-{chunk.page_end}"
        blocks.append(
            f"[{index}] {chunk.title} ({chunk.filename}{page_label})\n{chunk.text}"
        )
    return "\n\n".join(blocks)


def answer_question(
    client: OpenAI,
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> str:
    context = format_context(chunks)
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": f"Course materials:\n{context}\n\nStudent question:\n{question}",
        }
    )
    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def source_payload(chunks: list[RetrievedChunk]) -> list[dict[str, str | int | float | None]]:
    sources = []
    for index, chunk in enumerate(chunks, start=1):
        sources.append(
            {
                "citation_id": index,
                "title": chunk.title,
                "filename": chunk.filename,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "score": round(chunk.score, 4),
            }
        )
    return sources
