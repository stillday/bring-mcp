#!/usr/bin/env python3
"""Bring! MCP Server — manage Bring! shopping lists via Claude."""

import os

import aiohttp
from bring_api import Bring
from mcp.server.fastmcp import FastMCP

BRING_EMAIL = os.environ.get("BRING_EMAIL", "")
BRING_PASSWORD = os.environ.get("BRING_PASSWORD", "")

_session: aiohttp.ClientSession | None = None
_bring: Bring | None = None


async def get_bring() -> Bring:
    global _session, _bring
    if _bring is None:
        if not BRING_EMAIL or not BRING_PASSWORD:
            raise RuntimeError(
                "Bring! credentials missing. Set BRING_EMAIL and BRING_PASSWORD env vars."
            )
        _session = aiohttp.ClientSession()
        _bring = Bring(_session, BRING_EMAIL, BRING_PASSWORD)
        await _bring.login()
    return _bring


mcp = FastMCP("bring", host="0.0.0.0")


@mcp.tool()
async def get_lists() -> list[dict[str, str]]:
    """Alle Bring! Einkaufslisten abrufen."""
    bring = await get_bring()
    result = await bring.load_lists()
    return [
        {"uuid": lst.listUuid, "name": lst.name}
        for lst in result.lists
    ]


@mcp.tool()
async def get_list_items(list_uuid: str) -> dict[str, list[str]]:
    """Artikel einer Einkaufsliste abrufen.

    Args:
        list_uuid: UUID der Liste (aus get_lists)
    """
    bring = await get_bring()
    data = await bring.get_list(list_uuid)
    active = [
        item.itemId + (f" ({item.specification})" if item.specification else "")
        for item in data.items.purchase
    ]
    recently = [
        item.itemId + (f" ({item.specification})" if item.specification else "")
        for item in data.items.recently
    ]
    return {"active": active, "recently_purchased": recently}


@mcp.tool()
async def add_item(list_uuid: str, item_name: str, specification: str = "") -> str:
    """Artikel zur Einkaufsliste hinzufügen.

    Args:
        list_uuid: UUID der Liste (aus get_lists)
        item_name: Name des Artikels, z.B. "Milch"
        specification: Optionale Spezifikation, z.B. "3,5% Fett"
    """
    bring = await get_bring()
    await bring.save_item(list_uuid, item_name, specification)
    return f"'{item_name}' wurde zur Liste hinzugefügt."


@mcp.tool()
async def remove_item(list_uuid: str, item_name: str) -> str:
    """Artikel von der Einkaufsliste entfernen.

    Args:
        list_uuid: UUID der Liste (aus get_lists)
        item_name: Name des Artikels
    """
    bring = await get_bring()
    await bring.remove_item(list_uuid, item_name)
    return f"'{item_name}' wurde aus der Liste entfernt."


@mcp.tool()
async def complete_item(list_uuid: str, item_name: str) -> str:
    """Artikel als gekauft markieren (in 'Zuletzt gekauft' verschieben).

    Args:
        list_uuid: UUID der Liste (aus get_lists)
        item_name: Name des Artikels
    """
    bring = await get_bring()
    await bring.complete_item(list_uuid, item_name)
    return f"'{item_name}' wurde als gekauft markiert."


@mcp.tool()
async def add_items_bulk(list_uuid: str, items: list[dict[str, str]]) -> str:
    """Mehrere Artikel auf einmal zur Liste hinzufügen.

    Args:
        list_uuid: UUID der Liste (aus get_lists)
        items: Liste von Objekten mit 'name' und optionalem 'specification', z.B.
               [{"name": "Milch", "specification": "3,5%"}, {"name": "Brot"}]
    """
    bring = await get_bring()
    for item in items:
        await bring.save_item(list_uuid, item["name"], item.get("specification", ""))
    names = ", ".join(f"'{i['name']}'" for i in items)
    return f"{len(items)} Artikel hinzugefügt: {names}"


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        import uvicorn
        from starlette.responses import Response
        from starlette.types import ASGIApp, Receive, Scope, Send

        token = os.environ.get("MCP_TOKEN", "")
        port = int(os.environ.get("PORT", "8000"))

        class BearerTokenAuth:
            def __init__(self, app: ASGIApp) -> None:
                self.app = app

            async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
                if scope["type"] == "http" and token:
                    headers = dict(scope.get("headers", []))
                    auth = headers.get(b"authorization", b"").decode()
                    if not auth.startswith("Bearer ") or auth[7:] != token:
                        await Response(
                            '{"error":"unauthorized"}',
                            status_code=401,
                            media_type="application/json",
                        )(scope, receive, send)
                        return
                await self.app(scope, receive, send)

        uvicorn.run(BearerTokenAuth(mcp.streamable_http_app()), host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
