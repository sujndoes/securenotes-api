from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter 
from app.db import Base , engine
from app import models
from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.notes import router as notes_router

Base.metadata.create_all(bind = engine)
if settings.environment == "development":
	app = FastAPI()
else:
	app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def security_headers(request: Request, call_next):
	response = await call_next(request)
	response.headers["x-content-type-options"] = "nosniff"
	response.headers["x-frame-options"] = "DENY"
	response.headers["referrer-policy"] = "no-referrer"
	response.headers["cache-control"] = "no-store"
	
	return response

app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/health")
def health():
	return {"status":"ok"}
	

