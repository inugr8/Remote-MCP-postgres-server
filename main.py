import os
import threading
from typing import Optional

import uvicorn
from fastapi import FastAPI, Body, Query

from mcp_app import mcp

# --- Import tool implementations (they register with @mcp.tool for MCP) ---
import tools.list_schemas as t_list_schemas
import tools.list_objects as t_list_objects
import tools.get_object_details as t_get_object_details
import tools.explain_query as t_explain_query
import tools.analyze_workload_indexes as t_analyze_workload_indexes
import tools.analyze_query_indexes as t_analyze_query_indexes
import tools.analyze_db_health as t_analyze_db_health
import tools.get_top_queries as t_get_top_queries
import tools.execute_sql as t_execute_sql

# -----------------------------
# 1) Start FastMCP on loopback (internal only, for MCP clients)
# -----------------------------
INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = int(os.environ.get("MCP_INTERNAL_PORT", "9000"))

def run_mcp_in_thread():
    # Run FastMCP with HTTP transport internally (not exposed publicly)
    mcp.run(
        transport="http",
        host=INTERNAL_HOST,
        port=INTERNAL_PORT,
        path="/mcp",
        # log_level="info",
    )

mcp_thread = threading.Thread(target=run_mcp_in_thread, daemon=True)
mcp_thread.start()

# -----------------------------
# 2) Public FastAPI app (Actions-friendly)
# -----------------------------
app = FastAPI(
    title="PostgreSQL Deep Inspection Tools",
    description=(
        "REST facade for ChatGPT Actions. Endpoints call the same logic used by the MCP tools. "
        "Use /openapi.json to import into Custom GPT."
    ),
    version="1.0.0",
    servers=[{"url": "https://remote-mcp-postgres-server-1.onrender.com", "description": "Render"}],
)

@app.get("/", summary="Health")
def health():
    return {"ok": True, "message": "REST facade for FastMCP is running. See /openapi.json"}

# ---- REST endpoints mirroring your tools ----

@app.get("/schemas", summary="List schemas")
def schemas():
    return t_list_schemas.list_schemas()

@app.get("/objects", summary="List objects in a schema")
def objects(schema: str = Query("public")):
    return t_list_objects.list_objects(schema=schema)

@app.get("/object_details", summary="Get table details")
def object_details(table_name: str = Query(...), schema: str = Query("public")):
    return t_get_object_details.get_object_details(table_name=table_name, schema=schema)

@app.post("/explain_query", summary="EXPLAIN a query")
def explain_query(sql: str = Body(..., embed=True)):
    return t_explain_query.explain_query(sql=sql)

@app.post("/analyze_query_indexes", summary="Analyze query index usage (EXPLAIN)")
def analyze_query_indexes(sql: str = Body(..., embed=True)):
    return t_analyze_query_indexes.analyze_query_indexes(sql=sql)

@app.get("/analyze_db_health", summary="Basic DB health (table sizes)")
def analyze_db_health():
    return t_analyze_db_health.analyze_db_health()

@app.get("/get_top_queries", summary="Top queries from pg_stat_statements")
def get_top_queries(limit: int = Query(5, ge=1, le=100)):
    return t_get_top_queries.get_top_queries(limit=limit)

@app.post("/execute_sql", summary="Execute SELECT-only query")
def execute_sql(sql: str = Body(..., embed=True)):
    return t_execute_sql.execute_sql(sql=sql)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
