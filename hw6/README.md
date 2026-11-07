# Homework 6 - Offline password checker

Agent: **OpenAI Codex**, ChatGPT Work mode. Python 3.10+; no packages or keys.

From this folder:

```sh
python app.py --demo
python app.py
python -m unittest -v
```

On Linux/macOS use `python3` if `python` is unavailable. On Windows, `py`
also works. Interactive input is hidden and requires a real terminal.
Only use made-up examples, especially when recording.

## Behavior

- `Weak`: fewer than 10 characters, a built-in common password, or at most
  two distinct characters, regardless of length.
- `Moderate`: 10-15 characters or one of the checked obvious sequences.
- `Stronger candidate`: at least 16 characters without those simple flags.
- Empty input, more than 256 characters, and nonprintable characters fail.

The program returns only a rating, length, and advice. It does not include
the supplied password in its result object. Demo mode uses public fake samples.

## Security and limits

No network, database, file writes, eval, shell calls, or third-party packages.
User text is data. Rejecting control characters prevents terminal escape
sequences from being processed. Hidden-input fallback fails closed. Password
arguments are intentionally unsupported because they can expose secrets in
shell history and process listings. This is a local educational CLI, not a
public service or an authentication system.

The rating is a small rule-based heuristic, not an entropy estimate, breach
lookup, or guarantee. It can miss dictionary phrases, personal information,
predictable long passwords, and many patterns. The common list is tiny.
Use unique passwords and MFA. Python strings cannot reliably be erased from
memory; dropping a reference does not securely wipe it. The length check
occurs after terminal input is read, so it does not cap terminal memory use.

## Submission status

Code, tests, recorded original instructions, replay prompt, and recording
guide are prepared. `screencast_url.txt` is empty until the real video exists.
The document is a draft until genuine agent screenshots and the video URL
are added. The supplied course Word template has not been provided; if Canvas
requires that exact template, copy the prepared text into it.

Follow RECORDING_GUIDE.md. Do not submit the draft as complete.
