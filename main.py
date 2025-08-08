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

app = FastMCP(
    title="PostgreSQL Deep Inspection Tools",
    description="MCP tool server using fastMCP for schema introspection, index analysis, query execution.",
    version="1.0.0",
    tools=[
        list_schemas,
        list_objects,
        get_object_details,
        explain_query,
        analyze_workload_indexes,
        analyze_query_indexes,
        analyze_db_health,
        get_top_queries,
        execute_sql
    ]
)

if __name__ == "__main__":
    app.run()
