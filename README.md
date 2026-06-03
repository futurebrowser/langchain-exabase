# Exabase Monorepo

This repository uses a `uv` workspace layout.

The workspace root is virtual; it only coordinates the member packages.

Workspace members:

- `exabase` in `packages/exabase`
- `exabase-langchain` in `packages/langchain`

## Development

Install the workspace from the repository root:

```bash
uv sync
```

Run the LangChain examples:

```bash
uv run --package exabase-langchain python packages/langchain/examples/tools.py
```

Package-specific docs:

- [`packages/exabase/README.md`](packages/exabase/README.md)
- [`packages/langchain/README.md`](packages/langchain/README.md)
