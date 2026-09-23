from pathlib import Path

import pytest

from notes_loader import MarkdownSectionLoader, load_note
from langchain_core.documents import Document

from rag_engine import NotesRAG, chunk_id, collection_name, format_sources, prompt


def test_markdown_sections_keep_heading_path_and_ignore_fenced_headings(tmp_path: Path):
    note = tmp_path / "lecture.md"
    note.write_text("# Security\nIntro.\n## Threats\nCredential theft.\n```md\n# Fake\n```\n## Defense\nUse MFA.\n", encoding="utf-8")
    docs = MarkdownSectionLoader(note).load()
    assert [doc.metadata["section"] for doc in docs] == ["Security", "Security > Threats", "Security > Defense"]
    assert "# Fake" in docs[1].page_content
    assert docs[1].metadata["source"] == "lecture.md"


def test_empty_and_unsupported_files_are_rejected(tmp_path: Path):
    empty = tmp_path / "empty.txt"
    empty.write_text(" \n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_note(empty)
    unknown = tmp_path / "notes.exe"
    unknown.write_text("content", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_note(unknown)


def test_local_chroma_retrieves_numbered_sources_without_duplicates(tmp_path: Path):
    note = tmp_path / "lecture.md"
    note.write_text("# Authentication\nA passkey uses public key cryptography to resist phishing.\n", encoding="utf-8")
    rag = NotesRAG(tmp_path / "db")
    assert rag.index(note) == 1
    assert rag.index(note) == 0
    result = rag.ask("What resists phishing?")
    assert result["mode"] == "local"
    assert result["answer"] is None
    assert "passkey" in result["sources"][0].page_content
    assert "[1] lecture.md — Authentication" in format_sources(result["sources"])


def test_prompt_requires_context_and_admits_unknown():
    rendered = prompt.format_messages(question="What is a passkey?", context="[1] passkey note")
    assert "[1] passkey note" in rendered[0].content
    assert "don't know" in rendered[0].content
    assert "untrusted" in rendered[0].content.lower()


def test_skipped_heading_levels_do_not_keep_sibling_in_path(tmp_path: Path):
    note = tmp_path / "levels.md"
    note.write_text("# Root\nRoot text.\n### A\nA text.\n### B\nB text.\n", encoding="utf-8")
    assert [doc.metadata["section"] for doc in MarkdownSectionLoader(note).load()] == ["Root", "Root > A", "Root > B"]


def test_chunk_id_preserves_pdf_page_identity():
    first = Document(page_content="Same paragraph", metadata={"source": "notes.pdf", "page": 0})
    second = Document(page_content="Same paragraph", metadata={"source": "notes.pdf", "page": 1})
    assert chunk_id(first) != chunk_id(second)


def test_embedding_model_changes_collection_name():
    assert collection_name("google", "model-a") != collection_name("google", "model-b")
    assert collection_name("local") != collection_name("google", "model-a")


def test_google_mode_requires_chat_model_before_initializing_embeddings(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-project")
    monkeypatch.delenv("GOOGLE_MODEL", raising=False)
    with pytest.raises(ValueError, match="GOOGLE_MODEL"):
        NotesRAG(tmp_path / "db", mode="google")


def test_repeated_identical_chunks_index_once(tmp_path: Path):
    note = tmp_path / "repeats.txt"
    note.write_text("repeat " * 700, encoding="utf-8")
    rag = NotesRAG(tmp_path / "db")
    first_count = rag.index(note)
    assert first_count > 0
    assert rag.index(note) == 0
