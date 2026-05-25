# Foster MBA RAG Assistant MVP

This is a local demo MVP for the project proposal: a UW Foster MBA course-planning chatbot over the syllabus corpus.

## What it uses

- SQLite for the local demo database.
- OpenAI `text-embedding-3-small` to embed syllabus chunks and user queries.
- OpenAI `gpt-4.1-mini` for chat answers and the topic relevance agent.
- Flask for the web demo.

## Setup

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
python3 -m pip install -r requirements.txt
python3 ingest.py --reset
python3 app.py
```

Open http://127.0.0.1:5001.

You can also set the key directly in your shell:

```bash
export OPENAI_API_KEY="your_api_key"
```

The app also reads a local `open_ai_key.txt` file if `OPENAI_API_KEY` is not set. This file is listed in `.gitignore` and should not be committed.

## Optional configuration

```bash
export OPENAI_CHAT_MODEL="gpt-4.1-mini"
export OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
export DATABASE_PATH="./foster_mba_rag.sqlite3"
```

## Demo questions

- Which electives are most relevant if I want to go into corporate finance?
- What assignments are required in consumer insights?
- Which courses mention sustainability or climate risk?
- How are grades structured in the entrepreneurship courses?
