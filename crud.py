from sqlalchemy.orm import Session
import model


def create_user(db: Session, username: str, password: str):
    db_user = model.User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    return db.query(model.User).filter(model.User.username == username).first()


def create_note(db: Session, title: str, content: str, owner_id: int):
    db_note = model.Note(title=title, content=content, owner_id=owner_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_notes(db: Session, owner_id: int):
    return db.query(model.Note).filter(model.Note.owner_id == owner_id).all()


def update_note(db: Session, note_id: int, title: str, content: str):
    db_note = db.query(model.Note).filter(model.Note.id == note_id).first()
    if db_note:
        db_note.title = title
        db_note.content = content
        db.commit()
        db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int):
    db_note = db.query(model.Note).filter(model.Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note
