# langchain-exabase

Minimal LangChain integrations for Exabase memory.

## Install

```bash
uv add langchain-exabase
```

For local development:

```bash
uv sync
```

## What it provides

- `Exabase`: a small `requests`-based client for the Exabase memory API
- `ExabaseToolkit`: search, add, update, and remove memory tools
- `ExabaseStore`: a lightweight LangGraph/LangMem-compatible store adapter
- `ExabaseRetriever`: LangChain retriever backed by Exabase memory search
- `exabase_memory_middleware`: dynamic prompt middleware that injects relevant memories

## API notes

The client talks to the memory endpoints documented by Exabase:

- `POST /v2/memories`
- `POST /v2/memories/search` with a fallback to `GET /v2/memories/search`
- `GET /v2/memories/{memoryId}`
- `PATCH /v2/memories/{memoryId}` with a fallback to `PUT /v2/memories/{memoryId}`
- `DELETE /v2/memories/{memoryId}`

## Examples

See the `examples/` folder for one minimal script per feature.
