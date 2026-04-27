"""Zectrix API client."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


BASE_URL = "https://cloud.zectrix.com/open/v1"


@dataclass
class Device:
    device_id: str
    alias: str
    board: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        return cls(
            device_id=data["deviceId"],
            alias=data["alias"],
            board=data["board"],
        )


@dataclass
class Todo:
    id: int
    title: str
    description: str
    due_date: str
    due_time: str
    repeat_type: str
    status: int
    priority: int
    completed: bool
    device_id: str
    device_name: str
    create_date: str
    update_date: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Todo:
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("dueDate", ""),
            due_time=data.get("dueTime", ""),
            repeat_type=data.get("repeatType", "none"),
            status=data["status"],
            priority=data["priority"],
            completed=data["completed"],
            device_id=data["deviceId"],
            device_name=data.get("deviceName", ""),
            create_date=data.get("createDate", ""),
            update_date=data.get("updateDate", 0),
        )


class _DevicesAPI:
    def __init__(self, client: ZectrixClient) -> None:
        self._client = client

    def list(self) -> list[Device]:
        resp = self._client._request("GET", "/devices")
        return [Device.from_dict(d) for d in resp.get("data", [])]


class _TodosAPI:
    def __init__(self, client: ZectrixClient) -> None:
        self._client = client

    def list(
        self,
        *,
        status: int | None = None,
        device_id: str | None = None,
    ) -> list[Todo]:
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if device_id is not None:
            params["deviceId"] = device_id
        resp = self._client._request("GET", "/todos", params=params)
        return [Todo.from_dict(d) for d in resp.get("data", [])]

    def create(self, payload: dict[str, Any]) -> Todo:
        resp = self._client._request("POST", "/todos", json=payload)
        return Todo.from_dict(resp["data"])

    def update(self, todo_id: int, payload: dict[str, Any]) -> Todo:
        resp = self._client._request("PUT", f"/todos/{todo_id}", json=payload)
        return Todo.from_dict(resp["data"])

    def toggle_complete(self, todo_id: int) -> dict[str, Any]:
        return self._client._request("PUT", f"/todos/{todo_id}/complete")

    def delete(self, todo_id: int) -> dict[str, Any]:
        return self._client._request("DELETE", f"/todos/{todo_id}")


class _DisplayAPI:
    def __init__(self, client: ZectrixClient) -> None:
        self._client = client

    def push_image(
        self,
        device_id: str,
        *,
        images: list[tuple[str, bytes]],
        dither: bool = True,
        page_id: int | None = None,
    ) -> dict[str, Any]:
        files = [("images", (name, content, "image/png")) for name, content in images]
        data: dict[str, Any] = {"dither": str(dither).lower()}
        if page_id is not None:
            data["pageId"] = str(page_id)
        return self._client._request(
            "POST",
            f"/devices/{device_id}/display/image",
            data=data,
            files=files,
        )

    def push_text(
        self,
        device_id: str,
        text: str,
        *,
        page_id: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": text}
        if page_id is not None:
            payload["pageId"] = page_id
        return self._client._request(
            "POST",
            f"/devices/{device_id}/display/text",
            json=payload,
        )

    def push_structured_text(
        self,
        device_id: str,
        *,
        title: str,
        body: str,
        page_id: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title, "body": body}
        if page_id is not None:
            payload["pageId"] = page_id
        return self._client._request(
            "POST",
            f"/devices/{device_id}/display/structured-text",
            json=payload,
        )

    def delete_page(
        self,
        device_id: str,
        page_id: int | None = None,
    ) -> dict[str, Any]:
        path = f"/devices/{device_id}/display/pages"
        if page_id is not None:
            path += f"/{page_id}"
        return self._client._request("DELETE", path)


class ZectrixClient:
    """Zectrix API client."""

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=30.0,
        )

        self.devices = _DevicesAPI(self)
        self.todos = _TodosAPI(self)
        self.display = _DisplayAPI(self)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: list[Any] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        if params is not None:
            kwargs["params"] = params
        if json is not None:
            kwargs["json"] = json
        if data is not None:
            kwargs["data"] = data
        if files is not None:
            kwargs["files"] = files

        resp = self._http.request(method, path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> ZectrixClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
