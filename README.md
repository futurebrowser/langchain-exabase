# Exabase M-1 Memory Provider for LangChain

Exabase M-1 memory-provider integration for LangChain.

## About

[Exabase Memory (M-1)](https://exabase.io/memory) is a self-organising memory
engine for AI agents. It stores facts, preferences, and events, builds a living
knowledge graph, resolves contradictions, and evolves with every interaction.

M-1 is SOTA on the leading AI memory benchmark (LongMemEval), with the highest
recorded QA score, and using a small model. Read the research paper
[here](https://exabase.io/research/exabase-achieves-state-of-the-art-on-longmemeval-benchmark).


| System | Model | Score |
| --- | --- | --- |
| M-1 (Exabase) | Gemini 3 Flash | 96.4% |
| Mem0 | Gemini 3 Pro | 94.8% |
| Honcho | Gemini 3 Pro | 92.6% |
| HydraDB | Gemini 3 Pro | 90.79% |
| Supermemory | Gemini 3 Pro | 85.2% |

Exabase Memory powers memory in production apps like
[Fabric](https://fabric.so), used by 300,000+ people.

## Install

```bash
uv add langchain-exabase
```

For local development:

```bash
uv sync
```

## What it provides

- `ExabaseToolkit`: tools for searching, adding, updating, and removing Exabase
  memories
- `ExabaseStore`: a lightweight LangGraph/LangMem-compatible store adapter
- `ExabaseRetriever`: LangChain retriever backed by Exabase memory search
- `exabase_memory_middleware`: dynamic prompt middleware that injects relevant
  memories into conversations

## Examples

See the `examples/` folder for minimal scripts demonstrating each feature.
