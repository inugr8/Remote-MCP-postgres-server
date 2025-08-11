from db import get_connection
from mcp_app import mcp

@mcp.tool
def explain_query(sql: str) -> list[str]:
    """Run EXPLAIN on a read-only SQL query."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("EXPLAIN " + sql)
        plan = [row[0] for row in cur.fetchall()]
    except Exception as e:
        plan = [str(e)]
    finally:
        cur.close()
        conn.close()
    return plan
