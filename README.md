# Foster MBA Course Assistant

A course-planning chatbot for UW Foster MBA students. A student describes their goals or interests, and the assistant recommends which courses to take based on the actual syllabus content — and tells them when those courses are most likely offered based on past schedules.

> **Built by Jens Jung and Jimmy Yin (Foster MBA, Class of 2026) as a handoff project to the UW Foster MBA Program Office.**

---

## What it does

1. **Course recommendations from syllabi** — A student asks something like *"I want to go into venture capital"* or *"Which courses cover sustainability?"* and the assistant searches across all 49 course syllabi to find the best matches, explaining why each course fits.

2. **Schedule predictions from past offerings** — After answering, the assistant shows a green panel indicating which quarters a course has historically been offered (e.g., *"FIN 530: seen in Autumn (3×), Winter (2×) — most likely Autumn"*), based on 13 quarterly schedule PDFs from 2024–2026.

3. **Scope filtering** — Vague or off-topic questions are caught before they reach the AI. The assistant pushes back with a helpful suggestion on how to rephrase (e.g., *"Try asking: which courses cover corporate finance strategy?"*).

---

## How it works (non-technical summary)

- All course syllabi (PDF files) are read and broken into chunks of text.
- Each chunk is converted into a numerical "fingerprint" (called an embedding) by OpenAI.
- When a student asks a question, the question gets the same treatment and the closest-matching syllabus chunks are retrieved.
- Those chunks are sent to an OpenAI language model which writes a helpful answer with citations.
- Separately, the schedule PDFs are scanned for course codes to build a historical offering frequency map.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11 or later |
| pip | bundled with Python |
| OpenAI API key | [platform.openai.com](https://platform.openai.com) |

No database server, no Docker, no cloud account needed to run locally.

---

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/jimsteryin/fosterMBAbot.git
cd fosterMBAbot

# 2. Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
cp .env.example .env
# Open .env in any text editor and paste your key next to OPENAI_API_KEY=

# 5. Build the database from the syllabus PDFs
python3 ingest.py --reset

# 6. Start the web server
python3 app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

The status badge in the top-right corner turns green when the database is ready.

---

## Folder structure

```
fosterMBAbot/
├── Syllabus/          ← Course syllabus PDFs (source of truth for recommendations)
├── Schedules/         ← Quarterly schedule PDFs (source of truth for when predictions)
├── static/            ← Frontend CSS and JavaScript
├── templates/         ← HTML chat interface
├── app.py             ← Flask web server and API routes
├── ingest.py          ← Builds the SQLite vector database from syllabi
├── rag.py             ← Retrieval and answer generation
├── schedule_agent.py  ← Parses schedule PDFs and predicts quarter offerings
├── relevance_agent.py ← Filters off-topic or vague questions
├── config.py          ← Environment variable loading
├── db.py              ← SQLite schema and utilities
├── requirements.txt   ← Python dependencies
└── .env.example       ← Template for your environment variables
```

---

## Adding new syllabi

1. Drop the new PDF into the `Syllabus/` folder.
2. Re-run the ingest script:
   ```bash
   python3 ingest.py --reset
   ```
3. Restart `app.py`. No other changes needed.

The `--reset` flag clears and rebuilds the entire database. This takes about 1–3 minutes depending on the number of PDFs and your internet connection (OpenAI embedding calls are made per chunk).

---

## Adding new schedule files

1. Drop the new quarterly schedule PDF into the `Schedules/` folder.
2. Restart `app.py` (no ingest step needed — schedules are parsed at startup).

The schedule agent automatically detects the quarter from the filename. Files should include `AUT`, `WIN`, `SPR`, or `SUM` in the name (e.g., `AUT 2027 MBA Course Schedules.pdf`). Year-at-a-Glance files are skipped automatically.

---

## Shared file storage (Google Drive)

Syllabi and schedule PDFs are stored in a shared Google Drive folder so both collaborators and the program office can manage the files without needing a GitHub account:

**[Foster MBA Bot — Shared Folder](https://drive.google.com/drive/folders/1O-3lG8Q_FsWx-2x2hOx_M5AWKPNXNQeb)**

To use the latest files from Drive:
1. Download the `Syllabus/` and `Schedules/` folders from Drive.
2. Replace the local folders with the downloaded ones.
3. Re-run `python3 ingest.py --reset` and restart `app.py`.

The app itself reads files from the local disk. The Drive folder is a shared storage layer — it does not connect to the app directly. This keeps the setup simple and avoids API credentials for Drive.

---

## Example questions to try

- *"Which electives are most relevant if I want to go into corporate finance?"*
- *"What courses cover sustainability or ESG?"*
- *"I'm interested in entrepreneurship and startups — what should I take?"*
- *"How are grades structured in the marketing electives?"*
- *"What does MGMT 547 cover and when is it offered?"*
- *"Which courses mention consulting or case-based learning?"*

If a question is too vague (e.g., *"Tell me about business"*), the assistant will ask for a more specific question.

---

## Cost estimate (OpenAI API)

| Operation | Model | Approx. cost |
|-----------|-------|--------------|
| Initial ingest (49 syllabi) | text-embedding-3-small | ~$0.02 one-time |
| Per student question | gpt-4.1-mini + embedding | ~$0.002–0.005 |

At 1,000 questions per month, the running cost is roughly **$2–5/month**. The ingest only needs to run again when syllabi change.

---

## Program office: taking ownership

When the students who built this graduate, the program office will need to run and maintain this tool independently. Here is what that involves:

### 1. Get your own OpenAI API key
- Go to [platform.openai.com](https://platform.openai.com) and create an account.
- Under **API Keys**, create a new secret key.
- Paste it into your `.env` file as `OPENAI_API_KEY=sk-...`.
- Set a monthly spending limit in the OpenAI dashboard (we recommend $20/month to start).

### 2. Fork or copy the repository
- The code lives at [github.com/jimsteryin/fosterMBAbot](https://github.com/jimsteryin/fosterMBAbot).
- Either fork it to a UW Foster GitHub account or download the code as a ZIP and upload it to your own account.
- Create a new Google Drive folder under a Foster-managed Google account and update the link in this README.

### 3. Keep syllabi and schedules current
- Each academic year: download new syllabi from Canvas or course websites, add them to `Syllabus/`, and re-run `python3 ingest.py --reset`.
- Each quarter: add the new schedule PDF to `Schedules/` and restart `app.py`.

### 4. Hosting options (if you want students to access it online)
The app runs anywhere Python runs. Options in order of simplicity:

| Option | Cost | Notes |
|--------|------|-------|
| Run locally on a staff laptop | Free | Only accessible on that machine |
| [Render.com](https://render.com) | Free tier available | Push to GitHub → auto-deploys |
| [Railway.app](https://railway.app) | ~$5/month | Simple, no config needed |
| UW IT / AWS / Azure | Varies | Ask UW IT for student project hosting |

For any hosted deployment, set `OPENAI_API_KEY` as an environment variable in the hosting platform's dashboard rather than in a `.env` file.

### 5. No coding required for day-to-day use
The only recurring tasks are dropping new PDFs into the right folders and re-running the ingest script. No programming knowledge is required for that.

---

## Optional configuration

These can be set in `.env` or as shell environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_CHAT_MODEL` | `gpt-4.1-mini` | Language model for answers |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model for search |
| `DATABASE_PATH` | `./foster_mba_rag.sqlite3` | Where the SQLite DB is stored |
| `CHUNK_WORDS` | `420` | Words per syllabus chunk |
| `CHUNK_OVERLAP_WORDS` | `70` | Overlap between chunks |
| `TOP_K` | `8` | Number of chunks retrieved per query |

---

## Troubleshooting

**"Run ingest.py" badge stays yellow**
→ Run `python3 ingest.py --reset` and wait for it to finish before refreshing.

**`openai.AuthenticationError`**
→ Your `.env` file is missing `OPENAI_API_KEY` or the key is invalid. Check [platform.openai.com](https://platform.openai.com).

**Answer says "I don't have enough information"**
→ The relevant syllabus PDF may not be in `Syllabus/` or the database hasn't been rebuilt after adding it.

**Schedule prediction doesn't appear**
→ The course code wasn't found in any quarterly schedule PDF. Verify the PDF is in `Schedules/` and includes the quarter abbreviation in its filename.

---

## Tech stack

- **Python 3.11** / **Flask** — web server
- **OpenAI API** — embeddings (`text-embedding-3-small`) and chat (`gpt-4.1-mini`)
- **SQLite** — local vector + document store
- **PyPDF** — PDF text extraction
- **Vanilla HTML/CSS/JS** — no frontend framework

---

*Initial development: Jens Jung & Jimmy Yin, UW Foster MBA 2026*
