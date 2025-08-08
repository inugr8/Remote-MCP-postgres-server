from fastmcp import tool
from db import get_connection

@tool()
def execute_sql(sql: str) -> list[dict]:
    """
    Safely executes SELECT queries only.
    """
    if not sql.strip().lower().startswith("select"):
        return [{"error": "Only SELECT statements are allowed."}]

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()
    except Exception as e:
        result = [{"error": str(e)}]
    cur.close()
    conn.close()
    return result
