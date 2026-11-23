import json
import sqlite3
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    text: str


class Chat(BaseModel):
    title: str
    url: str
    messages: List[Message]


def get_db():
    conn = sqlite3.connect("memory.db")
    conn.row_factory = sqlite3.Row
    return conn


with get_db() as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS chats ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "title TEXT, url TEXT UNIQUE, messages TEXT)"
    )

def fingerprint(m):
    return m["role"] + "|" + m["text"].strip()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chats")
def save_chat(chat: Chat):
    if not chat.messages:
        raise HTTPException(status_code=400, detail="No messages to save")
    db = get_db()
    incoming = [m.model_dump() for m in chat.messages]

    old = db.execute("SELECT messages FROM chats WHERE url = ?", (chat.url,)).fetchone()
    merged = json.loads(old["messages"]) if old else []
    seen = {fingerprint(m) for m in merged}
    added = 0
    for m in incoming:
        if fingerprint(m) not in seen:
            merged.append(m)
            seen.add(fingerprint(m))
            added += 1

    db.execute(
        "INSERT INTO chats (title, url, messages) VALUES (?, ?, ?) "
        "ON CONFLICT(url) DO UPDATE SET "
        "title = excluded.title, messages = excluded.messages",
        (chat.title, chat.url, json.dumps(merged)),
    )
    db.commit()
    row = db.execute("SELECT id FROM chats WHERE url = ?", (chat.url,)).fetchone()

    return {"id": row["id"], "status": "saved", "new_messages": added,
            "messages_saved": len(merged)}


@app.get("/chats")
def list_chats():
    db = get_db()
    rows = db.execute("SELECT id, title, url FROM chats").fetchall()
    return [dict(r) for r in rows]


@app.get("/chats/{chat_id}")
def get_chat(chat_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    data = dict(row)
    data["messages"] = json.loads(data["messages"])
    return data


@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: int):
    db = get_db()
    cur = db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "deleted"}
