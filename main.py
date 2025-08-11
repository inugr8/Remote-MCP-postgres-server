import os
from mcp_app import mcp  # the shared server instance

# Import your tools purely for side-effects (registration via @mcp.tool).
# These imports must come AFTER mcp is created (happens in mcp_app)
import tools.list_schemas
import tools.list_objects
import tools.get_object_details
import tools.explain_query
import tools.analyze_workload_indexes
import tools.analyze_query_indexes
import tools.analyze_db_health
import tools.get_top_queries
import tools.execute_sql

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    # Use HTTP transport so host/port are valid on Render
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        # path="/",        # optional
        # log_level="info" # optional
    )
