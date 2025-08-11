import os
import threading
import asyncio
import uvicorn
import httpx

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse, Response
from starlette.routing import Route
from starlette.routing import Mount

from mcp_app import mcp  # your shared FastMCP instance

# -----------------------------
# 1) Start FastMCP on loopback
# -----------------------------
INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = int(os.environ.get("MCP_INTERNAL_PORT", "9000"))
INTERNAL_BASE = f"http://{INTERNAL_HOST}:{INTERNAL_PORT}"
MCP_PATH_PREFIX = "/mcp"  # where FastMCP will mount internally

def run_mcp_in_thread():
    # Run FastMCP HTTP server on 127.0.0.1:9000 (not exposed publicly)
    mcp.run(
        transport="http",
        host=INTERNAL_HOST,
        port=INTERNAL_PORT,
        path=MCP_PATH_PREFIX,   # internal mount
        # log_level="info",
    )

mcp_thread = threading.Thread(target=run_mcp_in_thread, daemon=True)
mcp_thread.start()

# ---------------------------------------
# 2) Front-facing Starlette shim (public)
# ---------------------------------------

async def root_ok(_req: Request):
    return PlainTextResponse("MCP shim is running. See /openapi.json, /tools, or /mcp/*")

async def openapi_proxy(_req: Request):
    # Always request JSON from the internal FastMCP server
    url = f"{INTERNAL_BASE}{MCP_PATH_PREFIX}/openapi.json"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"Accept": "application/json"})
        r.raise_for_status()
        return JSONResponse(r.json())

async def tools_proxy(_req: Request):
    url = f"{INTERNAL_BASE}{MCP_PATH_PREFIX}/tools"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"Accept": "application/json"})
        r.raise_for_status()
        return JSONResponse(r.json())

# Simple reverse proxy for /mcp/* so native endpoints are still reachable
async def mcp_proxy(req: Request):
    # Build target URL to internal FastMCP
    tail = req.url.path[len("/mcp"):] or "/"
    target = f"{INTERNAL_BASE}{MCP_PATH_PREFIX}{tail}"
    method = req.method.upper()

    headers = dict(req.headers)
    # Some clients won’t set Accept properly; pass through as-is
    content = await req.body()

    async with httpx.AsyncClient(timeout=None) as client:
        if method in ("GET", "DELETE"):
            r = await client.request(method, target, params=req.query_params, headers=headers)
        else:
            r = await client.request(method, target, params=req.query_params, headers=headers, content=content)

        # Stream SSE or other content if needed
        if r.headers.get("content-type", "").startswith("text/event-stream"):
            async def _aiter():
                async for chunk in r.aiter_bytes():
                    yield chunk
            return StreamingResponse(_aiter(), media_type="text/event-stream", headers={k: v for k, v in r.headers.items() if k.lower() != "content-length"})

        # Default: pass JSON or bytes through
        return Response(
            content=r.content,
            status_code=r.status_code,
            headers={k: v for k, v in r.headers.items() if k.lower() != "content-length"},
            media_type=r.headers.get("content-type")
        )

public_app = Starlette(
    routes=[
        Route("/", root_ok),
        Route("/openapi.json", openapi_proxy),
        Route("/tools", tools_proxy),
        # Catch-all for /mcp/* → internal FastMCP
        Route("/mcp", mcp_proxy),
        Route("/mcp/{path:path}", mcp_proxy),
    ]
)

if __name__ == "__main__":
    # Give the MCP server a moment to boot (best-effort)
    try:
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.2))
    except RuntimeError:
        pass

    PORT = int(os.environ.get("PORT", "8000"))  # Render-provided port
    uvicorn.run(public_app, host="0.0.0.0", port=PORT)
