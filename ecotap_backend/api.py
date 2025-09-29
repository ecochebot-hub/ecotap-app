from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from database import db

app = FastAPI(title="EcoTap API")

# Разрешаем фронтенду обращаться к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== FRONTEND ==================
@app.get("/")
async def serve_frontend():
    """Отдаёт index.html как главную страницу"""
    frontend_path = os.path.join(os.path.dirname(__file__), "../index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    raise HTTPException(status_code=404, detail="Frontend not found")

# ================== API ==================
@app.on_event("startup")
async def startup_event():
    await db.init_db()

@app.post("/api/register")
async def register_user(user: dict):
    user_id = user.get("user_id")
    username = user.get("username")
    first_name = user.get("first_name")
    last_name = user.get("last_name")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    registered = await db.register_user(user_id, username, first_name, last_name)
    progress = await db.get_user_progress(user_id)

    return {"registered": registered, "progress": progress}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    progress = await db.get_user_progress(user_id)
    if not progress:
        raise HTTPException(status_code=404, detail="User not found")
    return progress

@app.post("/api/tap")
async def tap(data: dict):
    user_id = data.get("user_id")
    taps = data.get("taps", 1)

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    result = await db.update_taps(user_id, taps)
    if not result:
        raise HTTPException(status_code=400, detail="Not enough energy or user not found")

    return result
