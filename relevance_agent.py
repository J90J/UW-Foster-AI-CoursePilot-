from __future__ import annotations

import json

from openai import OpenAI

from config import OPENAI_CHAT_MODEL


RELEVANCE_SYSTEM_PROMPT = """You are a strict scope-evaluation agent for a demo chatbot.
The product scope is the UW Foster MBA program course-planning assistant.
In-scope topics include Foster MBA courses, syllabi, elective selection, class schedules,
assignments, grading, instructors, MBA program information, and career-goal-based course
recommendations.
Out-of-scope topics include general homework unrelated to Foster MBA planning, politics,
medical/legal/financial advice, coding help, entertainment, personal data extraction, or
requests unrelated to MBA course planning.
Return only compact JSON with keys: in_scope (boolean), reason (string), suggested_rewrite (string)."""


def evaluate_relevance(client: OpenAI, message: str, history: list[dict] | None = None) -> dict[str, object]:
    messages: list[dict] = [{"role": "system", "content": RELEVANCE_SYSTEM_PROMPT}]
    # Include recent history so short follow-ups like "great. what else" are understood in context
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {
            "in_scope": False,
            "reason": "The scope evaluator returned an invalid response.",
            "suggested_rewrite": "Ask about Foster MBA courses, syllabi, grading, schedules, or electives.",
        }

    return {
        "in_scope": bool(parsed.get("in_scope")),
        "reason": str(parsed.get("reason") or "No reason provided."),
        "suggested_rewrite": str(
            parsed.get("suggested_rewrite")
            or "Ask about Foster MBA courses, syllabi, grading, schedules, or electives."
        ),
    }
