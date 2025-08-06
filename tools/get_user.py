from fastapi import APIRouter
from db import get_connection

router = APIRouter()

@router.get("/get_user")
def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {"id": row[0], "name": row[1], "role": row[2], "email": row[3]}
    return {"error": "User not found"}