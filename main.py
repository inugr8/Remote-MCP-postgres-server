# main.py
import os
import threading

import uvicorn
from fastapi import FastAPI, Body, Query
from fastapi.responses import JSONResponse

from mcp_app import mcp  # your shared FastMCP instance

# ----- Import tool implementations (register with @mcp.tool for MCP) -----
import tools.list_schemas as t_list_schemas
import tools.list_objects as t_list_objects
import tools.get_object_details as t_get_object_details
import tools.explain_query as t_explain_query
import tools.analyze_workload_indexes as t_analyze_workload_indexes
import tools.analyze_query_indexes as t_analyze_query_indexes
import tools.analyze_db_health as t_analyze_db_health
import tools.get_top_queries as t_get_top_queries
import tools.execute_sql as t_execute_sql

from db import get_connection  # used by /db_check

# -------------------------------------------------------------------------
# 1) Start FastMCP (HTTP transport) on loopback ONLY (for MCP-native clients)
# -------------------------------------------------------------------------
INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = int(os.environ.get("MCP_INTERNAL_PORT", "9000"))

def _run_mcp():
    # Runs a native MCP HTTP server (SSE/streaming capable) at /mcp internally.
    # This is not publicly exposed; the public app below is the REST facade.
    mcp.run(
        transport="http",
        host=INTERNAL_HOST,
        port=INTERNAL_PORT,
        path="/mcp",
        # log_level="info",
    )

threading.Thread(target=_run_mcp, daemon=True).start()

# -------------------------------------------------------------------------
# 2) Public FastAPI app (REST facade) — exposes /openapi.json for GPT import
# -------------------------------------------------------------------------
PUBLIC_BASE = os.environ.get("PUBLIC_BASE_URL", "https://remote-mcp-postgres-server-1.onrender.com")

app = FastAPI(
    title="PostgreSQL Deep Inspection Tools",
    description=(
        "REST facade for ChatGPT Actions. Endpoints call the same logic used by the MCP tools. "
        "Import this API in Custom GPT via /openapi.json."
    ),
    version="1.0.0",
    servers=[{"url": PUBLIC_BASE, "description": "Render"}],
)

@app.get("/", summary="Health")
def health():
    return {"ok": True, "message": "REST facade for FastMCP is running. See /openapi.json"}

@app.get("/db_check", summary="DB connectivity check")
def db_check():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT current_database() AS db, current_user AS user")
        row = cur.fetchone()
        cur.close(); conn.close()
        return {"ok": True, "db": row["db"], "user": row["user"]}
    except Exception as e:
        # Return the real reason so you can fix config quickly
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# ---- REST endpoints mirroring your tools (wrapped with error surfacing) ----

@app.get("/schemas", summary="List schemas")
def schemas():
    try:
        return t_list_schemas.list_schemas()
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/objects", summary="List objects in a schema")
def objects(schema: str = Query("public")):
    try:
        return t_list_objects.list_objects(schema=schema)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/object_details", summary="Get table details")
def object_details(table_name: str = Query(...), schema: str = Query("public")):
    try:
        return t_get_object_details.get_object_details(table_name=table_name, schema=schema)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/explain_query", summary="EXPLAIN a query")
def explain_query(sql: str = Body(..., embed=True)):
    try:
        return t_explain_query.explain_query(sql=sql)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/analyze_query_indexes", summary="Analyze query index usage (EXPLAIN)")
def analyze_query_indexes(sql: str = Body(..., embed=True)):
    try:
        return t_analyze_query_indexes.analyze_query_indexes(sql=sql)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/analyze_db_health", summary="Basic DB health (table sizes)")
def analyze_db_health():
    try:
        return t_analyze_db_health.analyze_db_health()
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/get_top_queries", summary="Top queries from pg_stat_statements")
def get_top_queries(limit: int = Query(5, ge=1, le=100)):
    try:
        return t_get_top_queries.get_top_queries(limit=limit)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/execute_sql", summary="Execute SELECT-only query")
def execute_sql(sql: str = Body(..., embed=True)):
    try:
        return t_execute_sql.execute_sql(sql=sql)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# -------------------------------------------------------------------------
# 3) Run the public REST app on Render's assigned port
# -------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
