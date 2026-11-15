# CodeGuardian – AI-Powered Code Review & Refactoring Agent

CodeGuardian is a learning project that reviews Python source code using syntax parsing,
built-in security/code-quality rules, optional Ruff and Bandit checks, and an optional
Groq-hosted LLM. It can generate a refactored version and syntax-validate that output.

## Architecture

- Frontend: Streamlit
- Backend: FastAPI
- Python parsing: `ast`
- Static analysis: Ruff and Bandit
- LLM: Groq API (optional)
- Validation: Python AST parse + compile (does not execute the submitted program)

## Requirements

Python 3.10+ recommended. On Windows, use two PowerShell terminals.

### 1. Backend

```powershell
cd CodeGuardian\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your own `GROQ_API_KEY`. The API still supports non-AI static review
without a key; AI review and refactoring require the key.

Start the API:

```powershell
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to inspect and test API endpoints.

### 2. Frontend

Open a second PowerShell terminal:

```powershell
cd CodeGuardian\frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The Streamlit app opens in your browser. By default it calls `http://127.0.0.1:8000`.
Set `API_URL` if your backend runs elsewhere.

## API endpoints

- `GET /health` – health status
- `POST /review` – review source code
- `POST /upload-review` – upload and review a `.py` file
- `POST /refactor` – generate refactored source and validate syntax
- `POST /validate` – syntax-validate source

Example JSON for `/review`:

```json
{
  "code": "def add(a, b):\n    return a + b",
  "use_ai": true
}
```

## Important safety and validation notes

- Uploaded code is treated as untrusted input.
- The service does not run user code or user tests.
- Ruff and Bandit inspect source statically.
- `compile()` checks syntax/compilability but does not execute the code.
- A syntactically valid refactor is not proof that behavior is preserved.
- For real execution-based tests, use a disposable, network-disabled container with
  strict CPU, memory, filesystem and time limits. Never execute untrusted code directly
  on the API host.
- Restrict CORS origins, add authentication/rate limits, and avoid logging secrets
  before deploying publicly.
