from fastmcp.tools import tool
from db import get_connection

@tool()
def explain_query(sql: str) -> list[str]:
    """
    Runs EXPLAIN on the provided SQL query (read-only).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("EXPLAIN " + sql)
        result = [row[0] for row in cur.fetchall()]
    except Exception as e:
        result = [str(e)]
    cur.close()
    conn.close()
    return result
