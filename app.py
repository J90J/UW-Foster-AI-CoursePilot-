from pathlib import Path

from flask import Flask, jsonify, render_template, request
from openai import OpenAI

from config import DATABASE_PATH
from db import connect, init_db
from rag import answer_question, retrieve, source_payload
from relevance_agent import evaluate_relevance


app = Flask(__name__)


def openai_client() -> OpenAI:
    return OpenAI()


def database_ready() -> bool:
    if not Path(DATABASE_PATH).exists():
        return False
    conn = connect()
    init_db(conn)
    count = conn.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()["count"]
    conn.close()
    return count > 0


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"database_ready": database_ready(), "database_path": str(DATABASE_PATH)})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("message", "")).strip()
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    if not database_ready():
        return (
            jsonify(
                {
                    "error": "The local RAG database has not been built yet.",
                    "next_step": "Run: python3 ingest.py --reset",
                }
            ),
            503,
        )

    try:
        client = openai_client()
    except Exception as error:
        return jsonify({"error": f"OpenAI client is not configured: {error}"}), 503

    relevance = evaluate_relevance(client, question)
    if not relevance["in_scope"]:
        return jsonify({"blocked": True, "relevance": relevance})

    chunks = retrieve(client, question)
    answer = answer_question(client, question, chunks)
    return jsonify(
        {
            "blocked": False,
            "answer": answer,
            "sources": source_payload(chunks),
            "relevance": relevance,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
