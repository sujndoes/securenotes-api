from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker , DeclarativeBase

from app.config import settings

engine = create_engine(
	settings.database_url,
	connect_args = {"check_same_thread":False},
)

SessionLocal = sessionmaker(autoflush = False, bind = engine)

class Base(DeclarativeBase):
	pass


def get_db():
		db = SessionLocal()
		try:
			yield db
		finally:
			db.close()	

@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()
