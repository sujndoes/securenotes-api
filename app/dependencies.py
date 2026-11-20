from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(access_token: str=Depends(oauth2_scheme), db:Session = Depends(get_db)):
	token_check = decode_access_token(access_token)
	if token_check is None:
		raise HTTPException(status_code=401, detail="Invalid or Expired Token", headers={"WWW-Authenticate": "Bearer"})
	current_user = db.scalar(select(User).where(User.id == token_check))
	if current_user is None:
		raise HTTPException(status_code=401,detail="Invalid or Expired Token", headers={"WWW-Authenticate": "Bearer"})
	return current_user	
			
