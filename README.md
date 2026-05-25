# Foster MBA Course Assistant

A course-planning chatbot for UW Foster MBA students. A student describes their goals or interests, and the assistant recommends which courses to take based on actual syllabus content — and tells them when those courses are most likely offered based on past schedules.

> **Built by Jens Jung and Jimmy Yin (Foster MBA, Class of 2026) as a handoff project to the UW Foster MBA Program Office.**

---

## What it does

1. **Course recommendations from syllabi** — A student asks something like *"I want to go into venture capital"* or *"Which courses cover sustainability?"* and the assistant searches across all course syllabi to find the best matches, explaining why each course fits.

2. **Schedule predictions from past offerings** — After answering, the assistant shows which quarters a course has historically been offered (e.g., *"FIN 530: seen in Autumn (3×), Winter (2×) — most likely Autumn"*), based on past quarterly schedule PDFs.

3. **Scope filtering** — Vague or off-topic questions are caught before they reach the AI. The assistant pushes back with a helpful suggestion on how to rephrase.

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
# Open .env and paste your key next to OPENAI_API_KEY=

# 5. Build the database from the syllabus PDFs
python3 ingest.py --reset

# 6. Start the web server
python3 app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

The status badge in the top-right turns green when the database is ready.

---

## Folder structure

```
fosterMBAbot/
├── Syllabus/          ← Course syllabus PDFs  ← ADD NEW SYLLABI HERE
├── Schedules/         ← Quarterly schedule PDFs  ← ADD NEW SCHEDULES HERE
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

The `--reset` flag clears and rebuilds the entire database. This takes about 1–3 minutes depending on the number of PDFs and your internet connection (OpenAI API calls are made per chunk).

---

## Adding new schedule files

1. Drop the new quarterly schedule PDF into the `Schedules/` folder.
2. Restart `app.py` (no ingest step needed — schedules are parsed at startup).

The schedule agent automatically detects the quarter from the filename. Files should include `AUT`, `WIN`, `SPR`, or `SUM` in the name (e.g., `AUT 2027 MBA Course Schedules.pdf`).

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
|-----------|-------|-------------|
| Initial ingest (49 syllabi) | text-embedding-3-small | ~$0.02 one-time |
| Per student question | gpt-4.1-mini + embedding | ~$0.002–0.005 |

At 1,000 questions per month, the running cost is roughly **$2–5/month**. The ingest only needs to run again when syllabi change.

---

## For the UW Foster MBA Program Office: Taking ownership

When the students who built this graduate, the program office will need to run and maintain this tool independently. This section explains everything you need to do.

### What you are taking over

This is a Python web application that runs on a server (or a laptop). It reads course syllabi from a folder of PDF files, builds a local search index, and serves a chat interface. There are no third-party subscriptions beyond OpenAI.

### Step 1 — Get your own OpenAI API key

- Go to [platform.openai.com](https://platform.openai.com) and create an account using a Foster/UW email.
- Under **API Keys**, create a new secret key. Copy it immediately — it is only shown once.
- Go to **Billing → Usage limits** and set a monthly spending limit (we recommend $20/month to start).
- Paste the key into your `.env` file as `OPENAI_API_KEY=sk-...`

### Step 2 — Fork the repository to a Foster-managed GitHub account

The code currently lives at [github.com/jimsteryin/fosterMBAbot](https://github.com/jimsteryin/fosterMBAbot) under a student account. You should copy it to an account you control so you don't lose access when the student graduates.

1. Create a GitHub account for the program office (e.g., `foster-mba-office`) if you don't have one.
2. Click **Fork** on the repository page — this creates your own copy.
3. Update the clone URL in this README to point to your fork.

### Step 3 — Set up your cloud environment

You have several options depending on your technical resources. All of them follow the same basic pattern: get a server running Python, clone the repo, configure the `.env` file, run the ingest script, and start the app.

**Option A — Run on a staff laptop (simplest, no cost)**

Only accessible on that machine. Good for demos or internal use.

```bash
git clone https://github.com/YOUR-ORG/fosterMBAbot.git
cd fosterMBAbot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in OPENAI_API_KEY
python3 ingest.py --reset
python3 app.py
```

**Option B — Deploy to Render.com (recommended for student-facing access)**

Render is a cloud hosting platform. The free tier is sufficient for low-traffic use.

1. Go to [render.com](https://render.com) and sign up with your GitHub account.
2. Click **New → Web Service** and connect your GitHub repository.
3. Set the following:
   - **Build Command:** `pip install -r requirements.txt && python ingest.py --reset`
   - **Start Command:** `python app.py`
4. Under **Environment**, add `OPENAI_API_KEY` with your key.
5. Click **Deploy**. Render gives you a public URL (e.g., `https://foster-mba-bot.onrender.com`).

**Option C — Deploy to Railway.app (~$5/month)**

Similar to Render but more reliable for always-on services.

1. Go to [railway.app](https://railway.app) and connect your GitHub repo.
2. Set `OPENAI_API_KEY` in the environment variables panel.
3. Railway auto-detects Python and deploys.

**Option D — Ask UW IT for hosting**

UW IT offers hosting for departmental projects. Contact the Foster School IT team and share this README — the app has no unusual infrastructure requirements (just Python 3.11 and outbound internet access for the OpenAI API).

### Step 4 — Keep syllabi and schedules current

This is the main ongoing task. No coding is required.

**Each time a new syllabus is available:**
1. Save the syllabus as a PDF.
2. Add it to the `Syllabus/` folder in your copy of the repository.
3. Run `python3 ingest.py --reset` on your server.
4. Commit the new PDF to GitHub so it is backed up: `git add Syllabus/ && git commit -m "Add new syllabus" && git push`

**Each quarter, when the new schedule is published:**
1. Save the schedule as a PDF with the quarter in the filename (e.g., `AUT 2027 MBA Course Schedules.pdf`).
2. Add it to the `Schedules/` folder.
3. Restart the app (the schedule is read at startup, no ingest needed).
4. Commit: `git add Schedules/ && git commit -m "Add AUT 2027 schedule" && git push`

### Step 5 — No coding required for day-to-day use

The only recurring tasks are dropping new PDFs into the right folders, running the ingest script, and restarting the app. A staff member with no programming background can do this by following the steps above.

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
→ Your `.env` is missing `OPENAI_API_KEY` or the key is invalid. Check [platform.openai.com](https://platform.openai.com).

**Answer says "I don't have enough information"**
→ The relevant syllabus PDF may not be in `Syllabus/` or the database hasn't been rebuilt after adding it.

**Schedule prediction doesn't appear**
→ The course wasn't found in any quarterly schedule PDF. Check that the schedule PDF is in `Schedules/` and includes `AUT`, `WIN`, `SPR`, or `SUM` in its filename.

---

## Tech stack

- **Python 3.11** / **Flask** — web server
- **OpenAI API** — embeddings (`text-embedding-3-small`) and chat (`gpt-4.1-mini`)
- **SQLite** — local vector + document store
- **PyPDF** — PDF text extraction
- **Vanilla HTML/CSS/JS** — no frontend framework

---

*Initial development: Jens Jung & Jimmy Yin, UW Foster MBA 2026*
