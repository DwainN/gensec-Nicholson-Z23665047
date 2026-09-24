"""FAU ID Z23665047: Chainlit notes browser adapted from 10_chainlit_rag_query.py.

The course's Chainlit start/message callbacks, Chroma retrieval, and
prompt/model/output-parser chain are retained through ``NotesRAG``. Uploading
notes, local retrieval, and a per-document source filter are added for this
homework.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import chainlit as cl

from notes_loader import SUPPORTED_SUFFIXES
from rag_engine import NotesRAG, format_sources


DATABASE = Path(__file__).parent / "data" / "chromadb"
DEMO_NOTE = Path(__file__).parent / "samples" / "demo_security_notes.md"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def engine(mode: str | None = None) -> NotesRAG:
    """Open the active mode's persistent Chroma collection for this session."""
    return NotesRAG(DATABASE, mode or cl.user_session.get("mode") or "local")


FILTER_ACTIONS = [
    cl.Action(name="filter_source", label="Filter by document", payload={"action": "filter"}),
]


def source_filter_label() -> str:
    """Describe the session's active source filter for display in a reply."""
    selected = cl.user_session.get("source_filter")
    return f"filtered to **{selected}**" if selected else "searching **all documents**"


@cl.on_chat_start
async def on_chat_start() -> None:
    """Explain the two modes and offer a file upload in the browser."""
    cl.user_session.set("mode", "local")
    cl.user_session.set("source_filter", None)
    await cl.Message(
        content=(
            "# Course Notes RAG\n\n"
            "**Local retrieval mode** is active. Upload a PDF, DOCX, TXT, or Markdown note, "
            "then ask a question. I will show relevant numbered excerpts; this mode does not "
            "generate an AI answer or use an API key.\n\n"
            "Use **Google answer mode** only if your Google Cloud environment is configured. "
            "It can incur cloud charges.\n\n"
            "By default I search **all** uploaded documents. Use **Filter by document** to "
            "restrict retrieval to one of them."
        ),
        actions=[
            cl.Action(name="upload_note", label="Upload note", payload={"action": "upload"}),
            cl.Action(name="load_demo", label="Load demo notes", payload={"action": "demo"}),
            cl.Action(name="switch_google", label="Google answer mode", payload={"action": "google"}),
            *FILTER_ACTIONS,
        ],
    ).send()


@cl.action_callback("load_demo")
async def load_demo(action: cl.Action) -> None:
    """Index bundled synthetic notes for an instant local demonstration."""
    try:
        count = engine().index(DEMO_NOTE)
        await cl.Message(
            content=(
                f"Loaded **synthetic demo notes** ({count} new excerpt(s)). "
                "Try: **How do passkeys resist phishing?**"
            )
        ).send()
    except Exception:
        await cl.Message(content="Could not load the bundled demo notes.").send()


@cl.action_callback("upload_note")
async def upload_note(action: cl.Action) -> None:
    """Ask for one note and index its extracted chunks."""
    files = await cl.AskFileMessage(
        content="Choose a PDF, DOCX, TXT, or Markdown note (up to 20 MB).",
        accept=[".pdf", ".docx", ".txt", ".md", ".markdown"],
        max_size_mb=20,
        max_files=1,
        timeout=300,
    ).send()
    if not files:
        return
    uploaded = files[0]
    filename = Path(uploaded.name).name
    if Path(filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        await cl.Message(content="Unsupported file type. Choose PDF, DOCX, TXT, or Markdown.").send()
        return
    if Path(uploaded.path).stat().st_size > MAX_UPLOAD_BYTES:
        await cl.Message(content="File exceeds the 20 MB upload limit.").send()
        return
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / filename
            shutil.copyfile(uploaded.path, path)
            count = engine().index(path, source_name=filename)
        if count:
            response = f"Indexed **{filename}**: {count} new excerpt(s). Ask a question about it."
        else:
            response = f"**{filename}** is already indexed; no duplicate excerpts were added."
    except ValueError as error:
        response = f"Could not index **{filename}**: {error}"
    except Exception:
        response = "Could not index this file. Check that it is a readable supported document."
    await cl.Message(content=response).send()


@cl.action_callback("filter_source")
async def filter_source(action: cl.Action) -> None:
    """Ask which indexed document to restrict retrieval to, or clear the filter.

    Lists the distinct ``source`` filenames currently indexed in the active
    mode's collection (see ``NotesRAG.list_sources``) as buttons, plus an
    "All documents" choice that clears the filter. The choice is stored in
    ``cl.user_session["source_filter"]`` and read by ``on_message``.
    """
    sources = engine().list_sources()
    if not sources:
        await cl.Message(content="No documents are indexed yet. Upload a note first.").send()
        return
    choices = [cl.Action(name="filter_choice", label="All documents", payload={"source": None})]
    choices += [
        cl.Action(name="filter_choice", label=name, payload={"source": name}) for name in sources
    ]
    response = await cl.AskActionMessage(
        content="Search which document?",
        actions=choices,
        timeout=120,
    ).send()
    if not response:
        return
    selected = response.get("payload", {}).get("source")
    cl.user_session.set("source_filter", selected)
    await cl.Message(content=f"Retrieval is now {source_filter_label()}.").send()


@cl.action_callback("switch_google")
async def switch_google(action: cl.Action) -> None:
    """Switch modes after confirming the Google configuration can initialize."""
    try:
        engine("google")
    except Exception:
        await cl.Message(
            content="Google mode is unavailable. Set GOOGLE_CLOUD_PROJECT and Google Application Default Credentials."
        ).send()
        return
    cl.user_session.set("mode", "google")
    cl.user_session.set("source_filter", None)
    await cl.Message(
        content="Google answer mode is active. Upload the same notes here before asking; this mode uses its own index.",
        actions=[
            cl.Action(name="upload_note", label="Upload note", payload={"action": "upload"}),
            cl.Action(name="switch_local", label="Local retrieval mode", payload={"action": "local"}),
            *FILTER_ACTIONS,
        ],
    ).send()


@cl.action_callback("switch_local")
async def switch_local(action: cl.Action) -> None:
    """Return to free local excerpt retrieval."""
    cl.user_session.set("mode", "local")
    cl.user_session.set("source_filter", None)
    await cl.Message(
        content="Local retrieval mode is active. Answers will show source excerpts only.",
        actions=[
            cl.Action(name="upload_note", label="Upload note", payload={"action": "upload"}),
            cl.Action(name="load_demo", label="Load demo notes", payload={"action": "demo"}),
            *FILTER_ACTIONS,
        ],
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Answer from retrieved notes and display the exact excerpts used."""
    source = cl.user_session.get("source_filter")
    try:
        result = engine().ask(message.content, source=source)
    except ValueError as error:
        await cl.Message(content=str(error)).send()
        return
    except Exception:
        await cl.Message(content="Query failed. Check the selected mode and try again.").send()
        return

    sources = format_sources(result["sources"])
    header = f"({source_filter_label()})"
    if result["mode"] == "local":
        content = f"**Local retrieval — source excerpts only (no AI-generated answer)** {header}\n\n" + sources
    else:
        content = f"**Google answer** {header}\n\n{result['answer']}\n\n**Retrieved source excerpts**\n\n{sources}"
    await cl.Message(content=content).send()
