from datetime import datetime , timedelta , timezone

import jwt

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

from app.config import settings
ALGORITHM = "HS256"

password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
	return password_hasher.hash(password)
	
	
def verify_password(stored_hash: str , password: str) -> bool:
	try:
		password_hasher.verify(stored_hash , password)
		return True
	except (VerificationError, InvalidHashError):
		return False
				
def create_access_token(user_id: int) -> str:
	expire = datetime.now(timezone.utc) + timedelta(minutes = settings.access_token_expire_minutes)
	payload = {"sub": str(user_id) , "exp": expire}
	return jwt.encode(payload , settings.secret_key , algorithm = ALGORITHM)
	
def decode_access_token(token: str) -> int | None:
	try:
		payload = jwt.decode(token , settings.secret_key , algorithms = [ALGORITHM], options={"require" : ["sub", "exp"]})
		return int(payload["sub"])
	except (jwt.PyJWTError , KeyError , ValueError):
		return None
