import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader

from config import CHUNK_OVERLAP_WORDS, CHUNK_WORDS, OPENAI_EMBEDDING_MODEL, SYLLABUS_DIR
from db import connect, encode_vector, init_db


@dataclass
class Chunk:
    text: str
    page_start: int
    page_end: int


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def title_from_filename(path: Path) -> str:
    title = path.stem.replace("_", " ").replace("-", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title


def extract_pdf_text(path: Path) -> tuple[list[tuple[int, str]], int]:
    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            pages.append((page_number, text))
    return pages, len(reader.pages)


def chunk_pages(pages: list[tuple[int, str]], chunk_words: int, overlap_words: int) -> list[Chunk]:
    words_with_pages: list[tuple[str, int]] = []
    for page_number, text in pages:
        words_with_pages.extend((word, page_number) for word in text.split())

    chunks: list[Chunk] = []
    if not words_with_pages:
        return chunks

    step = max(1, chunk_words - overlap_words)
    for start in range(0, len(words_with_pages), step):
        window = words_with_pages[start : start + chunk_words]
        if len(window) < 40 and chunks:
            break
        words = [word for word, _ in window]
        pages_in_window = [page for _, page in window]
        chunks.append(
            Chunk(
                text=" ".join(words),
                page_start=min(pages_in_window),
                page_end=max(pages_in_window),
            )
        )
    return chunks


def embed_texts(client: OpenAI, texts: list[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []
    batch_size = 64
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=batch)
        embeddings.extend(item.embedding for item in response.data)
    return embeddings


def embedding_input(title: str, filename: str, chunk: Chunk) -> str:
    return (
        f"Course document title: {title}\n"
        f"Source filename: {filename}\n"
        f"Pages: {chunk.page_start}-{chunk.page_end}\n\n"
        f"{chunk.text}"
    )


def ingest_documents(source_dir: Path, reset: bool) -> None:
    pdf_paths = sorted(source_dir.glob("*.pdf"))
    if not pdf_paths:
        raise SystemExit(f"No PDFs found in {source_dir}")

    client = OpenAI()
    conn = connect()
    init_db(conn)

    if reset:
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM documents")
        conn.commit()

    total_chunks = 0
    for path in pdf_paths:
        pages, page_count = extract_pdf_text(path)
        chunks = chunk_pages(pages, CHUNK_WORDS, CHUNK_OVERLAP_WORDS)
        if not chunks:
            print(f"Skipped {path.name}: no extractable text")
            continue

        title = title_from_filename(path)
        conn.execute("DELETE FROM documents WHERE filename = ?", (path.name,))
        cursor = conn.execute(
            "INSERT INTO documents (filename, title, pages) VALUES (?, ?, ?)",
            (path.name, title, page_count),
        )
        document_id = cursor.lastrowid

        embedding_texts = [embedding_input(title, path.name, chunk) for chunk in chunks]
        embeddings = embed_texts(client, embedding_texts)
        rows = [
            (
                document_id,
                index,
                chunk.page_start,
                chunk.page_end,
                chunk.text,
                encode_vector(embedding),
            )
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        conn.executemany(
            """
            INSERT INTO chunks
                (document_id, chunk_index, page_start, page_end, text, embedding_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
        total_chunks += len(chunks)
        print(f"Ingested {path.name}: {len(chunks)} chunks")

    conn.close()
    print(f"Done. Stored {total_chunks} chunks from {len(pdf_paths)} PDFs.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local SQLite RAG database.")
    parser.add_argument("--source-dir", type=Path, default=SYLLABUS_DIR)
    parser.add_argument("--reset", action="store_true", help="Clear existing indexed content first.")
    args = parser.parse_args()
    ingest_documents(args.source_dir, args.reset)


if __name__ == "__main__":
    main()
