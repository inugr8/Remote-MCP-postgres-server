import os
from fastmcp import FastMCP

from tools.list_schemas import list_schemas
from tools.list_objects import list_objects
from tools.get_object_details import get_object_details
from tools.explain_query import explain_query
from tools.analyze_workload_indexes import analyze_workload_indexes
from tools.analyze_query_indexes import analyze_query_indexes
from tools.analyze_db_health import analyze_db_health
from tools.get_top_queries import get_top_queries
from tools.execute_sql import execute_sql

TOOLS = [
    list_schemas,
    list_objects,
    get_object_details,
    explain_query,
    analyze_workload_indexes,
    analyze_query_indexes,
    analyze_db_health,
    get_top_queries,
    execute_sql,
]

# build the server and register tools (works across versions)
try:
    app = FastMCP(TOOLS)
except TypeError:
    app = FastMCP()
    add_many = getattr(app, "add_tools", None)
    add_one = getattr(app, "add_tool", None)
    if callable(add_many):
        add_many(TOOLS)
    elif callable(add_one):
        for t in TOOLS:
            add_one(t)
    else:
        setattr(app, "tools", TOOLS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    # IMPORTANT: run over HTTP transport so host/port are valid
    app.run(
        transport="http",         # or "streamable-http"
        host="0.0.0.0",
        port=port,
        # optional: path="/mcp/", log_level="info"
    )
