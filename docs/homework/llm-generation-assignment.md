# LLM Generation Homework (Gemini API)

## Goal

Implement one function to complete the middle API-call block in provider layer.

This homework trains you to:

- call external LLM API with SDK
- map external errors to domain errors
- validate model output contract

## Scope (Strict)

You should edit only one function:

- `app/services/providers/gemini_client.py`
  - `GeminiClient.generate_content(...)`

Do not modify:

- routes (`app/api/routes/*`)
- query orchestration (`app/services/query_service.py`)
- response schemas (`app/models/schemas.py`)

## Function Contract

Function to implement:

- `generate_content(prompt: str) -> str`

Input/output validation and API key checks are already prewritten for you.
Return validation is also prewritten for you.

You only need to implement the middle section that calls Gemini API.
`try/except` skeleton is already provided; write code inside `try` block only.

Important:

- JSON parsing is not done here (upper layer handles it)

## Required Behavior Checklist

Your implementation must do all items below:

1. create client with `genai.Client(api_key=api_key)`
2. call Gemini:
   - `model=settings.gemini_model`
   - `contents=prompt`
   - `config=types.GenerateContentConfig(...)` including:
     - `max_output_tokens=settings.llm_max_output_tokens`
     - `response_mime_type="application/json"`
3. catch `errors.APIError` and convert to `GeminiClientError`
4. catch other exceptions and convert to `GeminiClientError`

Skeleton location:

- `app/services/providers/gemini_client.py`
- function: `GeminiClient.generate_content(...)`
- marker comment: `# TODO(homework): implement only the API invocation block below.`

## Acceptance Criteria (Pass/Fail)

After implementation:

1. `POST /query` works and returns `answer` for a normal question
2. if provider API fails, code raises readable `GeminiClientError`
3. if provider returns empty text, code raises readable `GeminiClientError`
4. `/query` response schema stays unchanged

## Suggested Local Checks

Run backend:

```bash
python3 -m uvicorn app.main:app --reload
```

Run ingest once:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

Run query:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I reset my password?"}'
```

## Common Mistakes

1. not setting `response_mime_type="application/json"`
2. swallowing errors without converting to `GeminiClientError`
3. returning `response` object directly instead of `response.text`
4. changing files outside the provider homework scope
