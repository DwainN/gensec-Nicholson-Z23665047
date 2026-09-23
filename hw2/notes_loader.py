"""FAU ID Z23665047: load course files with useful source metadata.

This adapts the PDF, DOCX, and TXT loaders used in the course's
``07_rag_loaddb.py`` and adds a small Markdown BaseLoader for lecture headings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


SUPPORTED_SUFFIXES = {".md", ".markdown", ".pdf", ".docx", ".txt"}
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


class MarkdownSectionLoader(BaseLoader):
    """Return one document per Markdown heading section with its heading path."""

    def __init__(self, path: str | Path, source_name: str | None = None):
        self.path = Path(path)
        self.source_name = source_name or self.path.name

    def lazy_load(self) -> Iterator[Document]:
        """Parse ATX headings while treating fenced code as ordinary content."""
        lines = self.path.read_text(encoding="utf-8-sig").splitlines()
        headings: list[tuple[int, str]] = []
        content: list[str] = []
        section = "Overview"
        start_line = 1
        fence_char = ""
        fence_length = 0

        def current_doc() -> Document | None:
            body = "\n".join(content).strip()
            if not body:
                return None
            return Document(
                page_content=body,
                metadata={"source": self.source_name, "section": section, "line": start_line},
            )

        for line_number, line in enumerate(lines, 1):
            fence = FENCE.match(line)
            if fence:
                marker = fence.group(1)
                if not fence_char:
                    fence_char, fence_length = marker[0], len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_length:
                    fence_char, fence_length = "", 0
                content.append(line)
                continue

            heading = HEADING.match(line) if not fence_char else None
            if heading:
                document = current_doc()
                if document:
                    yield document
                level = len(heading.group(1))
                headings = [(depth, title) for depth, title in headings if depth < level]
                headings.append((level, heading.group(2).strip()))
                section = " > ".join(title for _, title in headings)
                content = []
                start_line = line_number + 1
            else:
                content.append(line)

        document = current_doc()
        if document:
            yield document


def load_note(path: str | Path, source_name: str | None = None) -> list[Document]:
    """Load one supported file and reject files without extractable text."""
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {path.suffix or '(none)'}")
    if not path.is_file():
        raise ValueError("File does not exist")
    if path.stat().st_size == 0:
        raise ValueError("File is empty")

    source = source_name or path.name
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        documents = MarkdownSectionLoader(path, source).load()
    elif suffix == ".pdf":
        documents = PyPDFLoader(str(path)).load()
    elif suffix == ".docx":
        documents = Docx2txtLoader(str(path)).load()
    else:
        documents = TextLoader(str(path), encoding="utf-8").load()

    documents = [doc for doc in documents if doc.page_content.strip()]
    if not documents:
        raise ValueError("File is empty or contains no extractable text")
    for doc in documents:
        doc.metadata["source"] = source
        doc.metadata.setdefault("section", "Overview")
    return documents
