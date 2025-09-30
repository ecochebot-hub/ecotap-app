from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="EcoTap API")

DB_PATH = os.getenv("DATABASE_PATH", "data/ecotap.db")

# ---------- Модели ----------
class RegisterRequest(BaseModel):
    user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class TapRequest(BaseModel):
    user_id: int
    taps: int = 1

# ---------- База данных ----------
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        points INTEGER DEFAULT 0,
        trees INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        energy INTEGER DEFAULT 100,
        total_taps INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# ---------- Роуты ----------
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"status": "EcoTap API running"}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "EcoTap API"}

@app.post("/api/register")
def register_user(req: RegisterRequest):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if get_user(req.user_id):
        return {"registered": False, "progress": get_user(req.user_id)}
    c.execute("""
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """, (req.user_id, req.username, req.first_name, req.last_name))
    conn.commit()
    conn.close()
    return {"registered": True, "progress": get_user(req.user_id)}

@app.post("/api/tap")
def tap(req: TapRequest):
    user = get_user(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    points = user["points"] + req.taps
    energy = max(user["energy"] - req.taps, 0)
    total_taps = user["total_taps"] + req.taps
    trees = points // 1000

    c.execute("""
        UPDATE users
        SET points=?, energy=?, total_taps=?, trees=?
        WHERE user_id=?
    """, (points, energy, total_taps, trees, req.user_id))
    conn.commit()
    conn.close()

    return get_user(req.user_id)

@app.get("/api/user/{user_id}")
def user_progress(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
