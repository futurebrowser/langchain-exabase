from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any, Iterable

from langgraph.store.base import (
    BaseStore,
    GetOp,
    Item,
    ListNamespacesOp,
    PutOp,
    SearchItem,
    SearchOp,
)

from .client import Exabase


def _namespace_text(namespace: Iterable[str]) -> str:
    return "/".join(namespace)


def _store_name(namespace: tuple[str, ...], key: str) -> str:
    return f"{_namespace_text(namespace)}::{key}"


def _store_content(namespace: tuple[str, ...], key: str, value: dict[str, Any]) -> str:
    return json.dumps({"namespace": list(namespace), "key": key, "value": value}, separators=(",", ":"))


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(tz=UTC)


def _decode_hit(hit: dict[str, Any]) -> Item | SearchItem | None:
    content = hit.get("content")
    if not isinstance(content, str):
        return None
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None
    namespace = tuple(payload.get("namespace") or ())
    key = payload.get("key")
    value = payload.get("value")
    if not namespace or not isinstance(key, str) or not isinstance(value, dict):
        return None
    created_at = _parse_datetime(hit.get("createdAt"))
    updated_at = _parse_datetime(hit.get("modifiedAt") or hit.get("updatedAt") or hit.get("createdAt"))
    score = hit.get("score")
    if score is not None:
        return SearchItem(
            namespace=namespace,
            key=key,
            value=value,
            created_at=created_at,
            updated_at=updated_at,
            score=score,
        )
    return Item(
        namespace=namespace,
        key=key,
        value=value,
        created_at=created_at,
        updated_at=updated_at,
    )


def _match_hit(hit: dict[str, Any], namespace: tuple[str, ...], key: str) -> bool:
    item = _decode_hit(hit)
    return bool(item and item.namespace == namespace and item.key == key)


class ExabaseStore(BaseStore):
    def __init__(self, client: Exabase) -> None:
        self.client = client

    def batch(self, ops: Iterable[Any]) -> list[Any]:
        return [self._dispatch_op(op) for op in ops]

    async def abatch(self, ops: Iterable[Any]) -> list[Any]:
        return [await asyncio.to_thread(self._dispatch_op, op) for op in ops]

    def _dispatch_op(self, op: Any) -> Any:
        if isinstance(op, GetOp):
            return self.get(op.namespace, op.key, refresh_ttl=op.refresh_ttl)
        if isinstance(op, SearchOp):
            return self.search(
                op.namespace_prefix,
                query=op.query,
                filter=op.filter,
                limit=op.limit,
                offset=op.offset,
                refresh_ttl=op.refresh_ttl,
            )
        if isinstance(op, PutOp):
            return self.put(
                op.namespace,
                op.key,
                op.value,
                index=op.index,
                ttl=op.ttl,
            )
        if isinstance(op, ListNamespacesOp):
            prefix = tuple()
            suffix = tuple()
            if op.match_conditions:
                for condition in op.match_conditions:
                    if condition.match_type == "prefix":
                        prefix = tuple(condition.path)
                    elif condition.match_type == "suffix":
                        suffix = tuple(condition.path)
            return self.list_namespaces(
                prefix=prefix or None,
                suffix=suffix or None,
                max_depth=op.max_depth,
                limit=op.limit,
                offset=op.offset,
            )
        raise TypeError(f"Unsupported store operation: {type(op)!r}")

    def put(
        self,
        namespace: tuple[str, ...] | list[str],
        key: str,
        value: dict[str, Any],
        index: Any = None,
        *,
        ttl: float | None = None,
    ) -> None:
        namespace = tuple(namespace)
        if value is None:
            self.delete(namespace, key)
            return
        query = _store_name(namespace, key)
        for hit in self.client.search_memories(query, limit=10).get("hits", []):
            if _match_hit(hit, namespace, key) and hit.get("id"):
                self.client.update_memory(
                    hit["id"],
                    content=_store_content(namespace, key, value),
                    name=_store_name(namespace, key),
                )
                return
        self.client.add_memory(
            _store_content(namespace, key, value),
            name=_store_name(namespace, key),
            infer=False,
            immutable=False,
        )

    async def aput(
        self,
        namespace: tuple[str, ...] | list[str],
        key: str,
        value: dict[str, Any],
        index: Any = None,
        *,
        ttl: float | None = None,
    ) -> None:
        await asyncio.to_thread(self.put, namespace, key, value, index, ttl=ttl)

    def get(
        self,
        namespace: tuple[str, ...],
        key: str,
        *,
        refresh_ttl: bool | None = None,
    ) -> Item | None:
        namespace = tuple(namespace)
        query = _store_name(namespace, key)
        for hit in self.client.search_memories(query, limit=10).get("hits", []):
            item = _decode_hit(hit)
            if item and item.namespace == namespace and item.key == key:
                return item
        return None

    async def aget(
        self,
        namespace: tuple[str, ...],
        key: str,
        *,
        refresh_ttl: bool | None = None,
    ) -> Item | None:
        return await asyncio.to_thread(self.get, namespace, key, refresh_ttl=refresh_ttl)

    def search(
        self,
        namespace_prefix: tuple[str, ...] | list[str],
        /,
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        namespace_prefix = tuple(namespace_prefix)
        query = query or _namespace_text(namespace_prefix)
        hits = self.client.search_memories(query, limit=max(limit * 5, limit), offset=offset).get("hits", [])
        items: list[SearchItem] = []
        for hit in hits:
            item = _decode_hit(hit)
            if isinstance(item, SearchItem) and item.namespace[: len(namespace_prefix)] == namespace_prefix:
                items.append(item)
            elif isinstance(item, Item) and item.namespace[: len(namespace_prefix)] == namespace_prefix:
                items.append(
                    SearchItem(
                        namespace=item.namespace,
                        key=item.key,
                        value=item.value,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                        score=hit.get("score"),
                    )
                )
            if len(items) >= limit:
                break
        return items

    async def asearch(
        self,
        namespace_prefix: tuple[str, ...] | list[str],
        /,
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        return await asyncio.to_thread(
            self.search,
            namespace_prefix,
            query=query,
            filter=filter,
            limit=limit,
            offset=offset,
            refresh_ttl=refresh_ttl,
        )

    def delete(self, namespace: tuple[str, ...] | list[str], key: str, **_: Any) -> None:
        namespace = tuple(namespace)
        query = _store_name(namespace, key)
        for hit in self.client.search_memories(query, limit=10).get("hits", []):
            if _match_hit(hit, namespace, key) and hit.get("id"):
                self.client.delete_memory(hit["id"])
                return

    async def adelete(self, namespace: tuple[str, ...] | list[str], key: str, **kwargs: Any) -> None:
        await asyncio.to_thread(self.delete, namespace, key, **kwargs)

    def list_namespaces(
        self,
        *,
        prefix: tuple[str, ...] | list[str] | None = None,
        suffix: tuple[str, ...] | list[str] | None = None,
        max_depth: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        prefix = tuple(prefix or ())
        suffix = tuple(suffix or ())
        hits = self.client.search_memories("", limit=limit).get("hits", [])
        namespaces: list[tuple[str, ...]] = []
        seen: set[tuple[str, ...]] = set()
        for hit in hits:
            item = _decode_hit(hit)
            if not isinstance(item, (Item, SearchItem)):
                continue
            ns = item.namespace
            if prefix and ns[: len(prefix)] != prefix:
                continue
            if suffix and ns[-len(suffix) :] != suffix:
                continue
            if ns not in seen:
                seen.add(ns)
                namespaces.append(ns)
        return namespaces[offset : offset + limit]

    async def alist_namespaces(
        self,
        *,
        prefix: tuple[str, ...] | list[str] | None = None,
        suffix: tuple[str, ...] | list[str] | None = None,
        max_depth: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        return await asyncio.to_thread(
            self.list_namespaces,
            prefix=prefix,
            suffix=suffix,
            max_depth=max_depth,
            limit=limit,
            offset=offset,
        )
