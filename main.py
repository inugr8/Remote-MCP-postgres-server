from fastapi import FastAPI
from tools import get_user, get_ticket, get_comments

app = FastAPI(
    title="PostgreSQL Support Tool",
    description="Use this tool to query user info, ticket status, and support comments from a PostgreSQL database.",
    version="1.0.0",
    servers=[
        {
            "url": "https://remote-mcp-postgres-server.onrender.com",  # ⬅️ Your deployed URL
            "description": "Public Render server"
        }
    ]
)

app.include_router(get_user.router)
app.include_router(get_ticket.router)
app.include_router(get_comments.router)
