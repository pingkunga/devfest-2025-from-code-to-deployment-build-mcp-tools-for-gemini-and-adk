# app/services/mcp.py
from __future__ import annotations

from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import settings

_client: MultiServerMCPClient | None = None
_cached_tools: List[BaseTool] | None = None


def _get_client() -> MultiServerMCPClient:
    global _client
    if _client is None:
        # Connect to the aggregator proxy (which fans out to many MCP servers)
        _client = MultiServerMCPClient(
            {
                "GoogleMap": {
                    "url": settings.MCP_GOOGLEMAP_URL,  # e.g. http://mcp-proxy:9090/mcp
                    "transport": "sse",  # matches proxy/server config
                },
                "FastMCP": {
                    "url": settings.MCP_CUSTOMFASTMCP_URL,
                    "transport": "streamable_http",
                },
            }
        )
    return _client


async def get_mcp_tools() -> List[BaseTool]:
    """Fetch and cache all tools exposed by the MCP proxy."""
    global _cached_tools
    if _cached_tools is None:
        client = _get_client()
        _cached_tools = await client.get_tools()
    return _cached_tools
