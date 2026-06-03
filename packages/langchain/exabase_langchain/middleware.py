from __future__ import annotations

from typing import Any

from langchain.agents.middleware import ModelRequest, dynamic_prompt

from exabase import Exabase
from .retriever import ExabaseRetriever


def _is_user_message(message: Any) -> bool:
    return (
        getattr(message, "type", None) == "human"
        or getattr(message, "role", None) == "user"
        or message.__class__.__name__ == "HumanMessage"
    )


def exabase_memory_middleware(
    client: Exabase | None = None,
    *,
    retriever: ExabaseRetriever | None = None,
    namespace: tuple[str, ...] = ("memories",),
    limit: int = 4,
) -> Any:
    if retriever is None:
        if client is None:
            raise ValueError("Provide either client or retriever.")
        retriever = ExabaseRetriever(client=client, limit=limit)

    @dynamic_prompt
    def memory_prompt(request: ModelRequest) -> str:
        messages = request.state.get("messages", [])
        query = ""
        for message in reversed(messages):
            if not _is_user_message(message):
                continue
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                query = content.strip()
                break
        if not query:
            return ""

        docs = retriever.invoke(query)
        if not docs:
            return ""

        lines = "\n".join(f"- {doc.page_content}" for doc in docs[:limit])
        scope = "/".join(namespace)
        if scope:
            return f"Relevant long-term memories for {scope}:\n{lines}"
        return f"Relevant long-term memories:\n{lines}"

    return memory_prompt
