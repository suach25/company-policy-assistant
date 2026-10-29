# Company Policy Assistant

A website that answers questions about company policies and compares three ways of finding answers.

## What the website does

Enter a question to see each method’s answer, the relevant policy, response time and AI token use. Tokens are pieces of text processed by the AI.

Visitors do not need to install software or provide an API key.

## The three methods

1. Word search: matches words in the question with words in the policies and returns the matching policy text.

2. AI with all policies: gives the question and all 98 policies to Gemini, which writes an answer.

3. AI with meaning search: finds the five closest policies by meaning, then gives their text to Gemini to write an answer.

## Policy data

The website uses the supplied collection of 98 company policies in data/company_policies.csv. It does not search the internet for company rules.

## Main files

| File or folder | Purpose |
|---|---|
| `app.py` | Runs the website’s server and handles questions. |
| `policy_engine.py` | Contains the three answering methods and contacts Gemini. |
| `web/index.html` | Contains the website’s layout and buttons. |
| `data/` | Contains the policies and saved information for meaning search. |
| `tests/` | Contains test questions, results and website checks. |
| `run_evaluation.py` | Runs the test questions and saves the results. |
| `EVALUATION.md` | Explains the testing and findings. |
| `requirements.txt` | Lists the Python packages the server needs. |
| `render.yaml`, `gunicorn.conf.py` and `.python-version` | Contain the online hosting settings. |
| `.gitignore` | Tells Git to leave out private and temporary files. |

## Testing

Each method was tested with the same 14 questions, producing 42 responses. The questions covered clear rules, different wording, missing information and misleading requests.

The coding assistant checked the answers against the policy text and recorded the findings. The saved results and review notes can be inspected on the website.

## Limitations

The policies are short and may not include every detail. The assistant can select the wrong policy or give an incomplete answer. The results from our 14 test questions do not guarantee that every future answer will be correct.

## API key

The application uses a private server-side Gemini API key. The key is not included in this repository or the website’s browser code.
