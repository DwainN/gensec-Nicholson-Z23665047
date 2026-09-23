# Course Notes RAG implementation plan

## Goal and constraints

Build a local NotebookLM-style application by directly adapting the instructor's
`02_LangChain/07_RAG/07_rag_loaddb.py`, `09_rag_query.py`, and
`10_chainlit_rag_query.py`. Original examples are preserved at instructor commit
`5c33afa1ed1147af463e23c1a544d8ff38ca8596`; the first homework commit copies the
Chainlit app verbatim so later diffs show the changes.

Use uv, Python docstrings, environment variables for credentials, and meaningful
incremental commits. Homework lives at repository-root `hw2` as instructed.

## Design

Keep the lab's load, split, Chroma retrieval, prompt, model, output-parser pipeline.
Add a custom BaseLoader for Markdown lecture notes that preserves heading paths
in metadata, numbered citations, retrieved excerpts, duplicate-safe indexing, and
a local browser interface. PDF, DOCX, TXT and Markdown ingestion are supported.
The custom Markdown loader and source presentation are the new functionality;
the original lab already supports PDF, DOCX and TXT.

Provide a clearly labeled local retrieval mode that runs without cloud credentials
and returns excerpts only. Google mode uses the course's Vertex embeddings and
Google chat model with environment configuration. Local mode must never pretend
to generate an AI answer. Store separate collections for incompatible embeddings.
Use a local-only server; display errors without leaking credential values.

## Task 1 Application and tests

- [ ] Add uv project configuration and lockfile.
- [ ] Write behavioral tests first for heading metadata, empty or unsupported
  files, source formatting, duplicate ingestion, retrieval and prompt grounding.
- [ ] Implement loader and reusable RAG engine in small documented modules.
- [ ] Adapt `app.py` into a browser interface for ingesting and querying notes.
- [ ] Add synthetic sample notes, explicitly labeled as demo data.
- [ ] Run tests and a real local retrieval smoke test, then commit working slices.

## Task 2 Documentation and submission preparation

- [ ] Explain original-code lineage and each extension in README.
- [ ] Document exact Windows uv launch steps and Google environment setup.
- [ ] Prepare VS Code prompts and evidence checklist, with ID Z23665047 visible.
- [ ] Prepare a five-minute screencast script following the required order.
- [ ] Populate the supplied Word template with known facts; clearly leave missing
  screenshots and video URL unfilled rather than inventing evidence.

## Task 3 Verification and handoff

- [ ] Independently review code and resolve material findings.
- [ ] Verify browser startup and local query behavior, and test a fresh local clone.
- [ ] Record exact checks and limitations. Cloud calls require configured credentials
  and authorization to spend; do not assert they ran if they did not.
- [ ] Leave a reviewable local branch and request publication approval at the end.

## Evidence limitations

This work began in the Codex desktop app. Desktop transcripts cannot be relabeled
as VS Code screenshots. The student must perform and capture genuine significant
agent tasks in VS Code and record their own narrated video with camera initially
on. The final PDF is submission-ready only once that real evidence is inserted.
