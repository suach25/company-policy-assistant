# Company Policy Assistant

A website that answers questions about company policies and compares three ways of finding answers.

## Three answering methods

- **Word search:** matches words in a question against policy titles and text, then returns the matching policy text.
- **AI with all policies:** gives the question and all 98 policies to Gemini to write an answer.
- **AI with meaning search:** uses saved numerical representations to find the five closest policies, then gives their text to the same Gemini model. This method is also called retrieval-augmented generation (RAG).

The comparison displays each answer, source policy text, response time and provider-reported token use. The saved evaluation includes 14 questions and 42 responses, with review notes explaining wrong sources, incomplete answers and irrelevant additions.

## Information source

`data/company_policies.csv` is the supplied dataset of 98 policies. `data/vector_index.json` stores their saved representations for meaning search. The system uses this collection as its evidence; it does not look up company rules on the internet.

## Files

| File or folder | Purpose |
|---|---|
| `app.py` | Serves the website and handles answer requests. |
| `policy_engine.py` | Implements the three methods and the Gemini requests. |
| `web/index.html` | Page layout, styling and browser interactions. |
| `data/` | Supplied policies and saved meaning-search index. |
| `run_evaluation.py` | Runs or resumes the 14-question evaluation with pauses between AI requests. |
| `tests/test_questions.json` | Questions, policy evidence and expected behavior. |
| `tests/evaluation_results.jsonl` | Actual evaluation responses and measurements. |
| `tests/evaluation_review.json` | Saved responses, review notes and summary displayed by the website. |
| `EVALUATION.md` | Evaluation method, results and limitations. |
| `requirements.txt` | Lists the Python packages needed to run the server. |
| `gunicorn.conf.py` | Sets the hosted server address, workers and timeouts. |
| `render.yaml` | Declares the free Render service, start command and private-key setting. |
| `.python-version` | Selects Python 3.12 for hosting. |
| `tests/test_web.py` | Checks page loading, HTTPS requests, input handling and private-file protection without Gemini requests. |
| `.gitignore` | Excludes secrets and temporary files when using Git. |

## Running a separate copy

This section is for a developer or reviewer running the source code. Ordinary visitors to the hosted website do not enter an API key or install software.

The application uses Python 3.12, Flask and Gunicorn. Install the packages with `python3 -m pip install -r requirements.txt`. Configure these server-side environment settings:

- `GEMINI_API_KEY`: a valid Gemini API key, stored privately.
- `GEMINI_MODEL`: `gemini-3.5-flash-lite`, the generation model used in the recorded evaluation.

Run `python3 app.py` from the repository folder, then open `http://127.0.0.1:8765`. This command is for local development. The hosted service runs `gunicorn app:app` using `gunicorn.conf.py` and the host-provided `PORT`. Debug mode is disabled.

The supplied index is complete. If the policy data or embedding model changes, rebuild it with `python3 -c "from policy_engine import build_index; build_index()"`. This makes Gemini API requests. The index uses `gemini-embedding-001` for policies and questions.

Run `python3 run_evaluation.py` to resume the saved evaluation or evaluate changed answering code. This uses API quota. It saves actual responses; it does not automatically judge their correctness or regenerate the reviewed summary. Review new results against the source policies before replacing the displayed evaluation.

## Hosting

This repository includes a Render configuration in `render.yaml`. It defines a free Python web service with:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check: `/health` (does not call Gemini)
- Private setting: `GEMINI_API_KEY`, entered in Render rather than committed to GitHub
- Model setting: `GEMINI_MODEL=gemini-3.5-flash-lite`

Create a Render web service from this GitHub repository, or use the included Blueprint configuration. The `.python-version` file selects the latest available Python 3.12 patch release. The supplied index is read-only during normal website use; a separate database or persistent disk is unnecessary.

Only the operator configures credentials. Visitors simply enter a policy question. Hosting preparation is complete, but a live deployment link must be verified separately; none is claimed in this source copy yet.

The free hosting plan pauses after 15 minutes of inactivity, so a first visit may take longer while it starts again. Gemini free-tier limits apply separately. The application allows one AI answer at a time and up to 12 AI answer requests per minute across visitors in its single server worker. This is a small shared coursework service, not a guarantee against all misuse or a billing cap. A restart clears the in-memory request counter.

## Website checks

Run `python3 -m unittest discover -s tests -p test_web.py`. These offline checks do not consume Gemini quota. The saved policy-answer evaluation is separate from these server checks; its answering code and recorded model have not changed in the hosting preparation.

## Limitations and review

The policies are short summaries and often omit details. Word matching can select the wrong policy. Meaning search can retrieve irrelevant evidence. AI can omit conditions or make unsupported claims. Missing information should be identified rather than filled from general knowledge. The system explains policies; it does not grant business approvals.

Recorded scores describe one designed 14-question test, not general accuracy. The review was performed by the coding assistant and should be checked by the student. Embedding token usage was not returned by the provider and is unavailable, not zero. One-time indexing is separate from per-question response time. Exact monetary cost has not been verified.

## Secrets

No real API key belongs in this repository or browser code. Store the key in the hosting service's private environment settings. The source also supports an untracked local `.env` file for development. `.gitignore` does not prevent someone from deliberately uploading secrets through a browser.
