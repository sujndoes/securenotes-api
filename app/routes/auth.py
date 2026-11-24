import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserOut, Token
from app.db import get_db
from app.models import User
from app.dependencies import get_current_user
from app.security import hash_password, verify_password, create_access_token
from app.limiter import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

DUMMY_HASH = hash_password("not-a-real-password")

@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
	ip = get_remote_address(request)
	email = data.email.lower().strip()
	check_email = db.scalar(select(User).where(User.email == email))
	if check_email is not None:
		logger.warning("duplicate_registration email=%r ip=%s", email, ip)
		raise HTTPException(status_code=409, detail="Email already used!")
		
	new_user = User(email=email, password_hash=hash_password(data.password))
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	
	return new_user
	
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	ip = get_remote_address(request)
	email = data.username.lower().strip()
	find_user = db.scalar(select(User).where(User.email==email))
	if find_user is None:
		verify_password(DUMMY_HASH, data.password)
		logger.warning("failed_login reason=unknown_user email=%r ip=%s", email, ip)
		raise HTTPException(status_code=401, detail="Incorrect Email or Password!")
	else:
		password_check = verify_password(find_user.password_hash, data.password)
		if password_check is False:
			logger.warning("failed_login reason=wrong_password email=%r ip=%s", email, ip)
			raise HTTPException(status_code=401, detail="Incorrect Email or Password!")
		else:
			logger.info("successful_login email=%r ip=%s", email, ip)
			return {"access_token" : create_access_token(find_user.id)}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
	return current_user		
