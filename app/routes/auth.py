from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserOut, Token
from app.db import get_db
from app.models import User
from app.dependencies import get_current_user
from app.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
	check_email = db.scalar(select(User).where(User.email == data.email))
	if check_email is not None:
		raise HTTPException(status_code=409, detail="Email already used!")
		
	new_user = User(email=data.email, password_hash=hash_password(data.password))
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	
	return new_user
	
@router.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	find_user = db.scalar(select(User).where(User.email==data.username))
	if find_user is None:
		raise HTTPException(status_code=401, detail="Incorrect Email or Password!")
	else:
		password_check = verify_password(find_user.password_hash, data.password)
		if password_check is False:
			raise HTTPException(status_code=401, detail="Incorrect Email or Password!")
		else:
			return {"access_token" : create_access_token(find_user.id)}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
	return current_user		
