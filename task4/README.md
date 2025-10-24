# AI Financial Support — Task4

Small CLI Python app that talks to Google GenAI (Gemini) to answer finance-related questions and extract user details.

This repository contains a simple interactive chatbot that:

-   Uses two Gemini API keys: one for general chat/generation and another for dedicated extraction tasks.
-   Keeps a running chat history in-memory and attempts to extract personal details from user inputs (name, account number, goal, contact, etc.).

This README documents how to set up, run, and troubleshoot the project.

## Contents

-   `app.py` — main CLI program and business logic
-   `requirements.txt` — Python dependencies
-   `.env` — (not committed) recommended place for API keys in development
-   `app2.ipynb` — an alternative notebook (if present)

## Quick start

1. Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the repository root with your keys (do NOT commit it):

```
GEMINI_API_KEY=your_primary_gemini_key_here
GEMINI_EXTRACTOR_API_KEY=your_extractor_gemini_key_here
```

4. Run the app:

```powershell
python .\app.py
```

The program will show a prompt. Type messages and it will reply. Type `exit` to quit.

## Environment variables

-   `GEMINI_API_KEY` — main API key used by the chat client.
-   `GEMINI_EXTRACTOR_API_KEY` — API key used for extraction calls.

Use a `.env` file during development and `python-dotenv` to load it. The project already imports `load_dotenv()` in `app.py`, so placing `.env` at the repo root is the simplest way.

Security: Add `.env` to `.gitignore` and never commit your secrets.

## Files and key functions (high level)

-   `app.py`
    -   `main()` — entrypoint that drives the interactive loop.
    -   `give_prompt(text_prompt)` — appends user to chat history and sends the prompt to the chat client.
    -   `extract_details(text_prompt)` — calls the model to extract structured details (expects JSON).
    -   `update_db(new_details)` — merges extracted details into local `user_db`.
    -   `history_append(role, text)` — helper that appends Content objects to `chat_history`.

## Suggested development improvements

-   Add unit tests for `update_db`, `extract_details` (mocking the API client) and `history_append`.
-   Add a config section to tune `MAX_HISTORY_TURNS` and `TEMPERATURE`.
-   Use the native chat interface with structured messages (role-aware) if the library supports it — that better preserves roles than concatenating text.
-   Persist `user_db` between runs (simple JSON file or SQLite) if you want long-lived user data.

## Troubleshooting

-   ValueError: `GEMINI_API_KEY not found.` — create `.env` and/or set the variable in your shell.
-   JSON decode error from `extract_details` — the model should return JSON; if it returns text, adjust `response_mime_type` or parse robustly and add retries.

## Example: set env in PowerShell (temporary session)

```powershell
$env:GEMINI_API_KEY = "your_key_here"
$env:GEMINI_EXTRACTOR_API_KEY = "your_extractor_key_here"
python .\app.py
```

## Example: persist env for new shells (Windows setx)

```powershell
setx GEMINI_API_KEY "your_key_here"
setx GEMINI_EXTRACTOR_API_KEY "your_extractor_key_here"
# restart PowerShell to pick up values
```

## setup.sh (helper script)

There is a small helper script `setup.sh` in the project root. Its current contents are:

```bash
docker build -t task4 .
docker run -it --rm --name task4 task4
```

Notes and recommendations:

-   The script builds the Docker image and runs a container, but it does NOT pass the required environment variables (`GEMINI_API_KEY`, `GEMINI_EXTRACTOR_API_KEY`). Running the container as-is will start the app without the API keys and it will raise an error.
-   Quick fix (PowerShell): pass your environment variables into the container when running:

```powershell
docker build -t task4 .
docker run -it --rm --name task4 \
    -e GEMINI_API_KEY="$env:GEMINI_API_KEY" \
    -e GEMINI_EXTRACTOR_API_KEY="$env:GEMINI_EXTRACTOR_API_KEY" \
    task4
```

-   POSIX-friendly `setup.sh` edit suggestion (if you want the script to forward host env vars):

```sh
docker build -t task4 .
docker run -it --rm --name task4 \
    -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
    -e GEMINI_EXTRACTOR_API_KEY="${GEMINI_EXTRACTOR_API_KEY}" \
    task4
```

-   Security: avoid baking secrets into the image. For production, use a secrets manager or docker secrets rather than plaintext env vars.

## Next steps I can help with

-   Apply the minimal code fixes to `app.py` (I can open a patch and update the file).
-   Add unit tests and a simple `pytest` config.
-   Add a JSON-backed `user_db` persistence and commands to dump/clear user data.

---

If you want, I can apply the code fixes now and run quick checks. Tell me which next step to perform.
