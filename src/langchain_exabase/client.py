from __future__ import annotations

from typing import Any

import requests


class ExabaseError(RuntimeError):
    pass


class Exabase:
    def __init__(
        self,
        api_key: str,
        base_id: str | None = None,
        base_url: str = "https://api.exabase.io",
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_id = base_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        if self.base_id:
            headers["X-Exabase-Base-Id"] = self.base_id

        response = self.session.request(
            method,
            f"{self.base_url}/v2/{path.lstrip('/')}",
            headers=headers,
            params=params,
            json=json_data,
            timeout=self.timeout,
        )
        if response.status_code == 204 or not response.content:
            return None
        if response.ok:
            return response.json()

        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise ExabaseError(f"{method} {path} failed: {response.status_code} {detail}")

    def add_memory(
        self,
        content: str,
        *,
        name: str | None = None,
        source: str = "text",
        infer: bool = True,
        immutable: bool = False,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "source": source,
            "content": content,
            "infer": infer,
            "immutable": immutable,
            "occurredAt": occurred_at,
        }
        if name is not None:
            payload["name"] = name
        return self._request("POST", "memories", json_data=payload) or {}

    def search_memories(
        self,
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        precision: float | None = None,
        expand_queries: int | None = None,
        rerank_candidates: int | None = None,
        rerank_threshold: float | None = None,
        order_property: str | None = None,
        order_direction: str = "ASC",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query, "limit": limit, "offset": offset}
        if precision is not None:
            params["precision"] = precision
        if expand_queries is not None:
            params["expandQueries"] = expand_queries
        if rerank_candidates is not None:
            params["rerankCandidates"] = rerank_candidates
        if rerank_threshold is not None:
            params["rerankThreshold"] = rerank_threshold
        if order_property is not None:
            params["property"] = order_property
            params["direction"] = order_direction
        payload = dict(params)
        last_error: ExabaseError | None = None
        for method, kwargs in (
            ("POST", {"json_data": payload}),
            ("GET", {"params": params}),
        ):
            try:
                return self._request(method, "memories/search", **kwargs) or {
                    "hits": [],
                    "total": 0,
                }
            except ExabaseError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        return {"hits": [], "total": 0}

    def get_memory(self, memory_id: str) -> dict[str, Any]:
        return self._request("GET", f"memories/{memory_id}") or {}

    def update_memory(
        self,
        memory_id: str,
        *,
        content: str,
        name: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {"content": content, "name": name}
        last_error: ExabaseError | None = None
        for method in ("PATCH", "PUT"):
            try:
                self._request(method, f"memories/{memory_id}", json_data=payload)
                return
            except ExabaseError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise ExabaseError(f"PATCH/PUT memories/{memory_id} failed")

    def delete_memory(self, memory_id: str) -> None:
        self._request("DELETE", f"memories/{memory_id}")

    def remove_memory(self, memory_id: str) -> None:
        self.delete_memory(memory_id)

    def get_memory_job(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"memories/jobs/{job_id}") or {}
