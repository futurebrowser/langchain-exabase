from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field

from .client import Exabase


class ExabaseRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: Exabase = Field(repr=False)
    limit: int = 4

    def _get_relevant_documents(self, query: str, *, run_manager: Any) -> list[Document]:
        hits = self.client.search_memories(query, limit=self.limit).get("hits", [])
        return [self._hit_to_document(hit) for hit in hits]

    async def _aget_relevant_documents(self, query: str, *, run_manager: Any) -> list[Document]:
        return self._get_relevant_documents(query, run_manager=run_manager)

    def _hit_to_document(self, hit: dict[str, Any]) -> Document:
        content = hit.get("content", "")
        metadata = {
            "id": hit.get("id"),
            "name": hit.get("name"),
            "score": hit.get("score"),
            "created_at": hit.get("createdAt"),
            "modified_at": hit.get("modifiedAt"),
            "indexed": hit.get("indexed"),
        }
        return Document(page_content=content, metadata=metadata)
