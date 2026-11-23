from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter 
from app.db import Base , engine
from app import models
from app.routes.auth import router as auth_router
from app.routes.notes import router as notes_router

Base.metadata.create_all(bind = engine)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/health")
def health():
	return {"status":"ok"}
	

