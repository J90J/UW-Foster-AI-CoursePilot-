import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

if not os.getenv("OPENAI_API_KEY"):
    key_file = BASE_DIR / "open_ai_key.txt"
    if key_file.exists():
        os.environ["OPENAI_API_KEY"] = key_file.read_text().strip()

SYLLABUS_DIR = BASE_DIR / "Syllabus"
SCHEDULES_DIR = BASE_DIR / "Schedules"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "foster_mba_rag.sqlite3"))

OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", "420"))
CHUNK_OVERLAP_WORDS = int(os.getenv("CHUNK_OVERLAP_WORDS", "70"))
TOP_K = int(os.getenv("TOP_K", "8"))
