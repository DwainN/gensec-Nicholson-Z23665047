# Course Notes RAG

Homework 2 · COT 4930 · Dwain Nicholson · Z23665047

A local notebook-style app for loading course notes and finding supporting
passages. Markdown sections retain their heading paths, so retrieved excerpts
show where the information came from. Google mode adds grounded answer generation.

## Start on Windows

Install Python and [uv](https://docs.astral.sh/uv/) if they are not already available.
From PowerShell:

```powershell
cd 'D:\school\COT 4930\gensec-code\hw2'
uv sync --locked
uv run chainlit run app.py --host 127.0.0.1 --port 8000
```

Open [the local app](http://127.0.0.1:8000). Local mode needs no API key. It returns
retrieved excerpts, **not an AI-generated answer**. The app binds to localhost;
it is intended for a single student's local demonstration.

For a fresh checkout, clone the homework branch from your course repository,
then enter `hw2` and run the same two uv commands:

```powershell
git clone --branch hw2-rag https://github.com/DwainN/gensec-Nicholson-Z23665047.git gensec-hw2-demo
cd gensec-hw2-demo\hw2
uv sync --locked
uv run chainlit run app.py --host 127.0.0.1 --port 8000
```

The branch must be pushed before the GitHub clone command can work. For the
screencast, run that clone from a new directory outside your working project.

## Where the code started

The original instructor files are preserved under `02_LangChain/07_RAG` at
upstream commit `5c33afa1ed1147af463e23c1a544d8ff38ca8596`:

| Instructor example | Derived homework behavior |
| --- | --- |
| `07_rag_loaddb.py` | Document loaders, RecursiveCharacterTextSplitter, Chroma indexing, Vertex embeddings |
| `09_rag_query.py` | Retrieval, context formatting, grounded prompt, chat model, StrOutputParser |
| `10_chainlit_rag_query.py` | Chainlit chat-start/message handlers and browser chat interface |

Commit `fdc1e1a` copies the instructor's Chainlit app verbatim into `hw2/app.py`.
Subsequent commits show the extensions. This is an adaptation of those examples,
not a separately generated replacement project.

## Custom functionality

- A custom Markdown loader extends LangChain `BaseLoader`, preserves hierarchical
  headings, and avoids treating fenced code as headings.
- Uploaded notes can be indexed interactively instead of editing the lab's fixed
  source list. PDF, DOCX, TXT, and Markdown are supported.
- Numbered excerpts include source metadata, making retrieved context inspectable.
- Repeated identical uploads do not add duplicate chunks.
- A local lexical retrieval mode supports development without cloud credentials.
  Google mode uses separate storage for its incompatible embedding vectors.

PDF, DOCX, and TXT support already existed in the instructor's loader example;
those formats alone are not claimed as original functionality.

## Demonstration

Load `samples/demo_security_notes.md`, which contains clearly labeled synthetic
course notes, then ask: **How do passkeys resist phishing?** Inspect the relevant
section and its numbered source excerpt. Upload the same file again to show
duplicate handling. Ask about a topic absent from the notes to show the limits
of retrieval.

## Google mode

Google mode uses billable cloud APIs and requires your course Google Cloud
configuration. Use the course's Application Default Credentials setup; do not
put service account keys or API keys in Python files or screenshots. Configure
these environment variables in the terminal used to launch the app:

```powershell
$env:GOOGLE_CLOUD_PROJECT = 'your-course-project-id'
$env:GOOGLE_CLOUD_LOCATION = 'us-west1'
$env:GOOGLE_EMBEDDING_MODEL = 'gemini-embedding-001'
$env:GOOGLE_MODEL = 'your-course-supported-chat-model'
```

Use a chat model actually enabled for your project and region. Environment values
above are configuration examples, not credentials or proof that a model is
available. Uploaded documents are sent to Google when using that mode.

## Verification

```powershell
uv run pytest -q
```

Tests exercise document handling, metadata, duplicates, retrieval, and the prompt
contract. Tests do not establish that cloud credentials, quotas, or current model
availability are valid. Live Google behavior must be checked with your authorized
course account before claiming it in the screencast.

## Limitations

Local retrieval uses lexical similarity and can miss synonyms or retrieve weak
matches. Scanned PDFs need OCR before ingestion. The application does not browse
the web or remember previous questions as conversation context. Grounding prompts
and source labels do not guarantee factual answers or defeat every prompt
injection; verify the actual excerpts. Keep files small enough for the app's
upload limits and your Google quota.

## Submission evidence

Follow [EVIDENCE.md](EVIDENCE.md) for the required VS Code screenshots, FAU ID,
recording order, YouTube accessibility check, and PDF checklist. Preparatory
Codex desktop work does not satisfy the VS Code screenshot requirement.
The Word report and recording must reflect actual work and actual results.
