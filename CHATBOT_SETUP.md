# AccessRoute Chatbot Setup

The assistant works in two modes:

1. **Grounded fallback** — works without an AI API key. It answers route, profile, obstacle, comparison, score, and confidence questions from the data supplied by AccessRoute.
2. **OpenAI mode** — if `OPENAI_API_KEY` is set in the backend `.env`, FastAPI sends the user's question plus the current route/profile context to the OpenAI Responses API. The browser never receives the secret key.

## Local setup

Create `Navigation/.env` and add:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6-luna
```

Restart FastAPI after changing `.env`.

The frontend stores the latest selected route context locally so the assistant can answer questions about the route selected on the Find Route page.

## Test endpoints

- `GET /api/chat/status`
- `POST /api/chat/message`

If no key is configured, `/api/chat/status` reports `deterministic_fallback` and the assistant remains usable.
