from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from model import Base, User, Note
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "postgresql://note_user:yourpassword@localhost/notes_app"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(SessionLocal)):
    username = request.cookies.get("username")
    if username:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return user
    return None


@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, register_username: str = Form(...), register_password: str = Form(...),
                   db: Session = Depends(get_db)):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == register_username).first()
    if existing_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username already taken"})

    # Create a new user with plain-text password
    new_user = User(username=register_username, password=register_password)
    db.add(new_user)
    db.commit()

    # Redirect back to the login page after successful registration
    return RedirectResponse("/", status_code=302)


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:
        response = RedirectResponse("/notes", status_code=302)
        response.set_cookie(key="username", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/notes", response_class=HTMLResponse)
async def get_notes(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/", status_code=302)
    notes = db.query(Note).all()
    return templates.TemplateResponse("main.html", {"request": request, "notes": notes})


@app.get("/create-note", response_class=HTMLResponse)
async def get_create_note_page(request: Request):
    return templates.TemplateResponse("create_note.html", {"request": request})


@app.post("/create-note", response_class=HTMLResponse)
async def create_note(request: Request, title: str = Form(...), description: str = Form(...),
                      db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_note = Note(
        title=title,
        description=description,
        created_at=datetime.now(),
        user_id=user.id
    )
    db.add(new_note)
    db.commit()

    # user.notes.append(new_note)
    # return templates.TemplateResponse("main.html", {"request": request, "notes": user.notes}, status_code=3020)

    return RedirectResponse("/notes", status_code=302)


@app.get("/edit-note/{note_id}", response_class=HTMLResponse)
async def get_edit_note_page(request: Request, note_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return templates.TemplateResponse("edit_note.html", {"request": request, "note": note, "note_id": note_id})


@app.post("/edit-note/{note_id}", response_class=HTMLResponse)
async def edit_note(request: Request, note_id: int, title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    note.title = title
    note.description = description
    note.created_at = datetime.now()
    db.commit()
    return RedirectResponse("/notes", status_code=302)


@app.post("/delete-note/{note_id}", response_class=HTMLResponse)
async def delete_note(request: Request, note_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.commit()
    return RedirectResponse("/notes", status_code=302)


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("username")
    return response
