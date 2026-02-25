# MyTeacher AI (Django + LangGraph + LangChain)

This repository provides an AI tutoring backend with:
- Django + DRF API
- Swagger UI via drf-spectacular
- End-to-end LangGraph workflow for normalization + decomposition
- LangChain + Azure OpenAI integration
- Structured JSON logging (structlog)
- Redis session-state storage
- Streamlit chat UI with live workflow keywords

## Setup (uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Swagger UI: `http://127.0.0.1:8000/api/docs/`

## Streamlit UI

```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

The UI behaves like a modern chat app and surfaces progress keywords to users:
- thinking
- transcribing
- extracting
- analyzing
- creating subgoals

## API Endpoints

### 1) Normalize only
`POST /api/v1/normalize/`

### 2) Decompose only
`POST /api/v1/decompose/`

### 3) Connected LangGraph workflow (recommended)
`POST /api/v1/workflow/`

Request:

```json
{
  "sessionId": "student-001",
  "inputType": "text",
  "text": "a) find velocity b) find acceleration"
}
```

Response:

```json
{
  "normalizedQuery": {
    "query": "a) find velocity b) find acceleration",
    "subject": "physics",
    "hasDiagram": false,
    "questionParts": ["find velocity", "find acceleration"],
    "metadata": {"inputType": "text"}
  },
  "decomposed": {
    "subgoals": ["find velocity", "find acceleration"],
    "currentIndex": 0
  },
  "statusTrail": [
    {"keyword": "thinking", "message": "Understanding your input format and preparing the workflow."},
    {"keyword": "analyzing", "message": "Analyzing the question intent and structure."},
    {"keyword": "creating subgoals", "message": "Creating the learning subgoals for this problem."}
  ]
}
```

If Azure OpenAI credentials exist, decomposition runs with structured LLM output. Else, it falls back to heuristics.
State is stored in Redis under `session:<sessionId>:decomposer`.
