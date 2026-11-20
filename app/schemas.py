from pydantic import BaseModel, EmailStr, Field, ConfigDict


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
