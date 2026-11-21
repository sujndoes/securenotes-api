from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
	email: EmailStr
	password: str =  Field(min_length=12 , max_length=255)
	
class UserOut(BaseModel):
	id: int
	email: EmailStr
	model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"

class NoteCreate(BaseModel):
	title: str = Field(min_length=1,max_length=255)
	body: str = Field(min_length=1,max_length=10000)
	
class NoteOut(BaseModel):
	id: int
	title: str
	body: str
	created_at: datetime
	model_config = ConfigDict(from_attributes=True)
