# Record once, under five minutes

Before recording: open a terminal and Codex, sign in to GitHub, and check
Python is installed. Use only fake examples. Prepare screen capture with
microphone and webcam. Keep generation small; rehearse once. Do not claim
the earlier preparation was an on-camera replay.

## 0:00-0:35 - Camera on and clone

Say: "I'm Dwain Nicholson. I used OpenAI Codex to build an offline Python
password checker from prompts. It uses the standard library."

Clone into a NEW folder (do not overwrite your existing course checkout):

```sh
git clone https://github.com/DwainN/gensec-Nicholson-Z23665047.git hw6-recording
cd hw6-recording/hw6
```

Private repository: authenticate normally; never show tokens on screen.

## 0:35-0:55 - Show prompts

Open prompts.txt. Explain the original short approval and that the longer
replay specification consolidates the design. Read the security requirements
briefly. Use the replay prompt section, not the historical context as a task.

## 0:55-2:40 - Actually regenerate

Make a clean sibling folder inside hw6 named replay. Open a NEW Codex session
scoped to that empty folder. Paste the replay prompt from prompts.txt. Let
Codex generate fresh app.py/test_app.py and run the checks. Do not simply
run the already-committed app and call that regeneration. If generation
exceeds the five-minute limit, simplify the prompt and record a new take.
Capture readable screenshots of the actual prompt and all agent replies,
including the generated-code views. Multiple images are better than tiny text.

## 2:40-3:45 - Demo

In the replay folder run the generated test command, then:

```sh
python app.py --demo
python app.py
```

Show common and repeated fake samples rated Weak, the long candidate, and
the overlength rejection. Type a fake value into hidden input; explain why
it does not echo. Generated code may differ, so use its actual run command.

## 3:45-4:40 - Explain security and limitations

Say in your own words: "It runs offline and doesn't save or print the input.
It avoids password command-line arguments and never executes what is typed.
It rejects control characters and invalid lengths. The rating is a simple
heuristic. It has a small common-password list, no breach database, and can
miss predictable long phrases. Python also can't guarantee clearing strings
from memory. A stronger label doesn't mean a password is safe."

## Finish after recording

1. Upload to YouTube as Unlisted, and verify playback while signed out or
   in incognito. Keep it no longer than five minutes.
2. Put the actual URL alone in hw6/screencast_url.txt.
3. Add the actual screenshots and URL to the Word draft (or required course
   template); export PDF. Save the replay prompt you actually used if changed.
4. Push the video URL and screenshots/replay files to the course repository.
5. Upload the completed PDF to the Homework Canvas page before its deadline.

The assignment page's countdown is not a verified Canvas due date; check
Canvas directly before deciding to delay submission.
