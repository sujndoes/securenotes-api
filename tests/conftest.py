import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app import models

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
	TEST_DATABASE_URL,
	connect_args = {"check_same_thread":False},
)

SessionLocal = sessionmaker(autoflush = False, bind = engine)

def override_get_db(): #function with test.db that will override any get_db call
		db = SessionLocal()
		try:
			yield db
		finally:
			db.close()	

@pytest.fixture
def client(): #should overrride any get_db call with override_get_db , uses test.db instead of securenotes.db
	app.dependency_overrides[get_db] = override_get_db
	Base.metadata.create_all(bind = engine)
	try:
			yield TestClient(app)
	finally:
			Base.metadata.drop_all(bind = engine)
			app.dependency_overrides.clear()
