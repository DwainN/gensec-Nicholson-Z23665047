# Course Notes RAG

Upload a PDF, Word document, text file, or Markdown note using **Upload note**.
Ask a question after the app confirms that the note is indexed.

**Local retrieval mode** returns numbered excerpts from your notes. It does not
generate an AI answer and needs no API key. A heading next to each Markdown
excerpt identifies its section in the original note.

**Google answer mode** generates an answer from retrieved context using the
course Google Cloud setup. It requires credentials, can incur charges, and sends
your document text to Google. Each mode has a separate index, so upload your notes
again after switching modes.

Always compare an answer with its source excerpts. Local keyword similarity can
miss synonyms or surface irrelevant passages; scanned PDFs require OCR first.

Homework 2, COT 4930 — Dwain Nicholson — Z23665047
