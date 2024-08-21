from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Example in-memory store
users = {"1": "1"}
notes = []


class NoteCreate(BaseModel):
    title: str
    description: str


@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if users.get(username) == password:
        return templates.TemplateResponse("main.html", {"request": request, "notes": notes})
    return HTMLResponse("Invalid credentials", status_code=401)


@app.get("/logout")
async def logout():
    return RedirectResponse(url="/")


@app.get("/create-note", response_class=HTMLResponse)
async def get_create_note_page(request: Request):
    return templates.TemplateResponse("create_note.html", {"request": request})


@app.post("/create-note")
async def create_note(request: Request, title: str = Form(...), description: str = Form(...)):
    note = {
        "title": title,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    notes.append(note)
    return templates.TemplateResponse("main.html", {"request": request, "notes": notes})


@app.get("/edit-note/{note_id}", response_class=HTMLResponse)
async def get_edit_note_page(request: Request, note_id: int):
    note = notes[note_id]
    return templates.TemplateResponse("edit_note.html", {"request": request, "note": note, "note_id": note_id})


@app.post("/edit-note/{note_id}")
async def edit_note(note_id: int, title: str = Form(...), description: str = Form(...)):
    notes[note_id] = {
        "title": title,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return templates.TemplateResponse("main.html", {"request": request, "notes": notes})


@app.post("/delete-note/{note_id}")
async def delete_note(note_id: int, request: Request):
    global notes
    notes = [note for index, note in enumerate(notes) if index != note_id]
    return templates.TemplateResponse("main.html", {"request": request, "notes": notes})
