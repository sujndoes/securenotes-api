from fastapi import FastAPI
from app.db import Base , engine

from app import models

Base.metadata.create_all(bind = engine)
app = FastAPI()

@app.get("/health")

def health():
	return {"status":"ok"}
