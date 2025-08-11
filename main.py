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

# 1) Construct the server with NO positional args
app = FastMCP()

# 2) Register tools (support both API shapes)
if hasattr(app, "add_tools") and callable(app.add_tools):
    app.add_tools(TOOLS)
elif hasattr(app, "add_tool") and callable(app.add_tool):
    for t in TOOLS:
        app.add_tool(t)
else:
    # Fallback for very old versions
    app.tools = TOOLS

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    # Run over HTTP so host/port are valid on Render
    app.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        # path="/",           # optional
        # log_level="info",   # optional
    )
