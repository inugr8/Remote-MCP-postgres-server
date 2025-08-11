from db import get_connection
from mcp_app import mcp

@mcp.tool
def execute_sql(sql: str) -> list[dict]:
    """Safely execute SELECT-only SQL and return rows."""
    if not sql.strip().lower().startswith("select"):
        return [{"error": "Only SELECT statements are allowed."}]

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        rows = [{"error": str(e)}]
    finally:
        cur.close()
        conn.close()
    return rows
