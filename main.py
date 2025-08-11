import os
import uvicorn
import httpx
from httpx import ASGITransport
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route, Mount

from mcp_app import mcp  # shared FastMCP instance

# Import tools ONLY for side effects (registration via @mcp.tool)
import tools.list_schemas
import tools.list_objects
import tools.get_object_details
import tools.explain_query
import tools.analyze_workload_indexes
import tools.analyze_query_indexes
import tools.analyze_db_health
import tools.get_top_queries
import tools.execute_sql

# Build FastMCP HTTP ASGI app and mount under /mcp
mcp_http_app = mcp.build_http_app()  # FastMCP 2.x

# --- JSON shims so browsers & GPT Actions always get JSON ---
async def root_ok(_request):
    return PlainTextResponse("MCP server is running. See /openapi.json or /mcp/*")

async def openapi_proxy(_request):
    async with httpx.AsyncClient(transport=ASGITransport(app=mcp_http_app)) as client:
        r = await client.get("/openapi.json", headers={"Accept": "application/json"})
    return JSONResponse(r.json())

async def tools_proxy(_request):
    async with httpx.AsyncClient(transport=ASGITransport(app=mcp_http_app)) as client:
        r = await client.get("/tools", headers={"Accept": "application/json"})
    return JSONResponse(r.json())

parent = Starlette(
    routes=[
        Route("/", root_ok),
        Route("/openapi.json", openapi_proxy),
        Route("/tools", tools_proxy),
        Mount("/mcp", app=mcp_http_app),
    ]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(parent, host="0.0.0.0", port=port)
