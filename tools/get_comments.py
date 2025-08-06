from fastapi import APIRouter
from db import get_connection

router = APIRouter()

@router.get("/get_comments")
def get_comments(ticket_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM support_comments WHERE ticket_id = %s", (ticket_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"id": r[0], "author": r[1], "content": r[2]} for r in rows]