from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas import NoteOut, NoteCreate
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User, Note

router = APIRouter()

@router.post("/notes", response_model=NoteOut, status_code=201)
def post_notes(data: NoteCreate, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
	new_note = Note(title=data.title, body=data.body, owner_id=current_user.id)
	db.add(new_note)
	db.commit()
	db.refresh(new_note)
	
	return new_note

@router.get("/notes",response_model=list[NoteOut], status_code=200)                     #200 for OK status
def get_notes(db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
	notes_list = db.scalars(select(Note).where(Note.owner_id==current_user.id)).all()
	return notes_list

@router.get("/notes/{note_id}", response_model=NoteOut, status_code=200)
def get_notes_id(note_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
	selected_note = db.scalar(select(Note).where(Note.id == note_id).where(Note.owner_id == current_user.id))  #this makes sure users cannot access others notes using note id
	if selected_note:
		return selected_note
	raise HTTPException(status_code=404, detail="Not Found")

@router.put("/notes/{note_id}", response_model=NoteOut, status_code=200)
def put_notes_id(data:NoteCreate, note_id:int, db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
	selected_note = db.scalar(select(Note).where(Note.id == note_id).where(Note.owner_id == current_user.id))
	if selected_note is None:
		raise HTTPException(status_code=404, detail="Not Found")
	selected_note.title = data.title
	selected_note.body = data.body
	db.commit()
	db.refresh(selected_note)
	return selected_note
	
@router.delete("/notes/{note_id}", status_code=204)          #204 No content
def delete_notes_id(note_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
	selected_note = db.scalar(select(Note).where(Note.id == note_id).where(Note.owner_id == current_user.id))
	if selected_note is None:
		raise HTTPException(status_code=404, detail="Not Found")
	db.delete(selected_note)
	db.commit()
