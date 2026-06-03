from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool, tool
from langchain_core.tools.base import BaseToolkit
from pydantic import ConfigDict, Field

from exabase import Exabase


class ExabaseToolkit(BaseToolkit):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: Exabase = Field(repr=False)

    def get_tools(self) -> list[BaseTool]:
        client = self.client

        @tool("exabase_search_memories")
        def search_memories(query: str, limit: int = 10) -> str:
            """Search Exabase memories."""
            return json.dumps(client.search_memories(query, limit=limit), indent=2)

        @tool("exabase_add_memory")
        def add_memory(
            content: str,
            name: str | None = None,
            infer: bool = False,
            immutable: bool = False,
        ) -> str:
            """Add a memory to Exabase."""
            return json.dumps(
                client.add_memory(
                    content,
                    name=name,
                    infer=infer,
                    immutable=immutable,
                ),
                indent=2,
            )

        @tool("exabase_update_memory")
        def update_memory(memory_id: str, content: str, name: str | None = None) -> str:
            """Update a memory by id."""
            client.update_memory(memory_id, content=content, name=name)
            return json.dumps({"ok": True, "memory_id": memory_id}, indent=2)

        @tool("exabase_remove_memory")
        def remove_memory(memory_id: str) -> str:
            """Delete a memory by id."""
            client.remove_memory(memory_id)
            return json.dumps({"ok": True, "memory_id": memory_id}, indent=2)

        return [
            search_memories,
            add_memory,
            update_memory,
            remove_memory,
        ]
