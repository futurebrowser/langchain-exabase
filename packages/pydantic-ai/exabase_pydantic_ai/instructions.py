from typing import Any
from collections.abc import Callable

from pydantic_ai import RunContext
from exabase import Exabase


def exabase_memory_instructions(
    client: Exabase,
    *,
    query: str = "relevant context about the user",
    limit: int = 5,
    precision: float | None = None,
    rerank_candidates: int | None = None,
    prefix: str = "Relevant memories:\n",
) -> Callable[[RunContext[Any]], str]:
    """Create an instructions function that auto-injects relevant memories.

    Returns a function suitable for use with Pydantic AI's
    ``instructions`` parameter.

    Args:
        client: The Exabase client.
        query: The search query to find relevant memories.
        limit: Maximum number of memories to include.
        precision: Search precision threshold (0.0 to 1.0).
        rerank_candidates: Number of candidates to rerank.
        prefix: Text prepended before the memory list.

    Returns:
        A function compatible with ``Agent(instructions=[...])``.
    """

    def _instructions(ctx: RunContext[Any]) -> str:
        try:
            response = client.search_memories(
                query=query,
                limit=limit,
                precision=precision,
                rerank_candidates=rerank_candidates,
            )
            hits = response.get("hits", [])
            if not hits:
                return ""

            lines = [prefix]
            for i, hit in enumerate(hits, 1):
                content = hit.get("content", "")
                lines.append(f"{i}. {content}")
            return "\n".join(lines)
        except Exception:
            # Silently return empty — instructions failures shouldn't block the agent
            return ""

    return _instructions
