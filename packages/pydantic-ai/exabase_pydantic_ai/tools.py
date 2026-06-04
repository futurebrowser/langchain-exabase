import logging

from pydantic_ai import Tool
from exabase import Exabase


logger = logging.getLogger(__name__)


def create_exabase_tools(
    client: Exabase,
    *,
    include_add: bool = True,
    include_search: bool = True,
    search_limit: int = 5,
    search_precision: float | None = None,
    search_rerank_candidates: int | None = None,
) -> list[Tool]:
    """Create Exabase memory tools for a Pydantic AI agent.

    Returns a list of ``Tool`` instances that can be passed directly to
    ``Agent(tools=...)``.

    Args:
        client: The Exabase client.
        include_add: Include the tool to add memories.
        include_search: Include the tool to search memories.
        search_limit: Maximum number of memories to return when searching.
        search_precision: Search precision threshold (0.0 to 1.0).
        search_rerank_candidates: Number of candidates to rerank.

    Returns:
        List of Pydantic AI Tool instances.
    """
    tools: list[Tool] = []

    if include_add:
        def exabase_add_memory(content: str) -> str:
            """Store information to long-term memory for later retrieval.

            Use this to save important facts, user preferences, decisions,
            or any information that should be remembered across conversations.
            """
            try:
                client.add_memory(content=content)
                return "Memory stored successfully."
            except Exception as e:
                logger.error(f"Exabase add_memory failed: {e}")
                return f"Error storing memory: {e}"

        tools.append(Tool(exabase_add_memory, takes_ctx=False))

    if include_search:
        def exabase_search_memories(query: str) -> str:
            """Search long-term memory for relevant information.

            Use this to find previously stored facts, preferences, or context.
            Returns a list of matching memories.
            """
            try:
                response = client.search_memories(
                    query=query,
                    limit=search_limit,
                    precision=search_precision,
                    rerank_candidates=search_rerank_candidates,
                )
                hits = response.get("hits", [])
                if not hits:
                    return "No relevant memories found."

                lines = []
                for i, hit in enumerate(hits, 1):
                    content = hit.get("content", "")
                    lines.append(f"{i}. {content}")
                return "\n".join(lines)
            except Exception as e:
                logger.error(f"Exabase search_memories failed: {e}")
                return f"Error searching memories: {e}"

        tools.append(Tool(exabase_search_memories, takes_ctx=False))

    return tools
