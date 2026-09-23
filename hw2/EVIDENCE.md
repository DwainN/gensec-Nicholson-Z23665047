# Homework 2 evidence checklist

Student: Dwain Nicholson — Z23665047

## What still needs to happen in VS Code

The homework requires a coding agent **inside VS Code**. The preparatory work in
Codex desktop is not a substitute for that requirement. Capture genuine agent
work as it happens; do not label suggested prompts as prompts already executed.

Open this repository in VS Code and open `hw2/app.py`. Keep `Z23665047` visible
in the code editor or a visible evidence note in every screenshot. Do not expose
API keys, credential files, terminal history containing secrets, or `.env` values.

For every significant task you actually give the VS Code coding agent:

1. Paste the actual prompt as text into the supplied Word template.
2. Capture the VS Code window with that prompt and the agent's actual response.
3. Capture the VS Code window with at least the top lines of the changed code.
4. Make sure your FAU ID is readable in both screenshots.
5. Insert both screenshots immediately below that task's prompt.
6. Save a meaningful commit, then explain its diff in the recording.

## Suggested next agent task

This is a suggested prompt, not evidence of completed work:

> My FAU ID is Z23665047. Extend the Homework 2 Course Notes RAG app with a source
> filter so I can restrict retrieval to one uploaded document or search all
> documents. First explain the existing retrieval pipeline and where it comes
> from in 02_LangChain/07_RAG. Implement the filter with docstrings and tests
> that verify documents from other sources are excluded. Keep the existing
> local and Google modes working. Do not expose credentials. Show me the changed
> code and explain the limitations so I can capture the required screenshots.

Capture additional significant tasks you actually perform, including fixes or
improvements after testing. Review and understand every generated change.

## Recording order and time budget

Keep the total recording below five minutes and turn the camera on initially.

- 0:00–0:20: introduce yourself, your FAU ID, and the app with camera on.
- 0:20–1:00: run `git clone` from your GitHub repository into a **new directory
  outside the existing project**. Enter `hw2`, run `uv sync`, then launch the app.
  Dependencies can be cached before the recording, but show the actual clone.
- 1:00–2:35: demonstrate loading notes, asking a supported question, reviewing
  source excerpts, and uploading the same file again. Explain the custom loader.
- 2:35–3:10: demonstrate a limitation, such as an unrelated question. State that
  local mode returns excerpts and Google mode generates answers. For a full RAG
  demonstration, configure and test Google mode before recording.
- 3:10–4:50: show each homework commit diff on GitHub. Explain the lab baseline,
  custom loader, retrieval and citations, interface, tests, and limitations.

Use the exact launch instructions in README.md. Show real results, including any
limitations; do not describe an untested cloud path as verified.

## Publication and submission

- Push the reviewed homework branch to the course repository before class.
- Verify that the repository URL in the report leads to the submitted code.
- Record your own narrated screencast in the sequence above.
- Upload to YouTube as **unlisted** and check playback in an incognito window
  without signing in.
- Put the recording URL in `hw2/screencast_url.txt` and in the Word report.
- Add your actual screenshots and prompts to `hw2-Z23665047.docx`.
- Replace every remaining angle-bracket field and verify all screenshots are
  readable, show your FAU ID, and reflect actual work.
- Export to `hw2-Z23665047.pdf`, inspect every page, then upload that PDF to Canvas.

The repository, video publication, and Canvas submission require the student's
review. This file is a checklist, not proof that these steps have occurred.
