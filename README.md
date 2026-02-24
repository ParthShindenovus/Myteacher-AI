# MyTeacher AI (Django + LangGraph + LangChain)

This repository provides an AI tutoring backend with:
- Django + DRF API
- Swagger UI via drf-spectacular
- LangGraph workflow for question decomposition
- LangChain + Azure OpenAI integration
- Structured JSON logging (structlog)
- Redis session-state storage

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

## Implemented Phases

### Phase 1 — Input Understanding Layer
`POST /api/v1/normalize/`

Supported payload:

```json
{
  "inputType": "text",
  "text": "a) find velocity b) find acceleration"
}
```

Response:

```json
{
  "query": "a) find velocity b) find acceleration",
  "subject": "physics",
  "hasDiagram": false,
  "questionParts": ["find velocity", "find acceleration"],
  "metadata": {
    "inputType": "text"
  }
}
```

### Phase 2 — Question Decomposer
`POST /api/v1/decompose/`

```json
{
  "sessionId": "student-001",
  "normalizedQuery": {
    "query": "find velocity and acceleration",
    "subject": "physics",
    "hasDiagram": false,
    "questionParts": []
  }
}
```

If Azure OpenAI credentials exist, decomposition runs with structured output. Else, it falls back to simple heuristics.
State is stored in Redis under `session:<sessionId>:decomposer`.
