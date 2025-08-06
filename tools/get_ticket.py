from fastapi import APIRouter
from db import get_connection

router = APIRouter()

@router.get("/get_ticket")
def get_ticket(ticket_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {"id": row[0], "title": row[1], "category": row[2], "status": row[3]}
    return {"error": "Ticket not found"}