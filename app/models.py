from datetime import datetime , timezone
from sqlalchemy import ForeignKey , String , Text
from sqlalchemy.orm import Mapped , mapped_column , relationship

from app.db import Base

class User(Base):
	__tablename__ = "users"
	
	id: Mapped[int] = mapped_column(primary_key = True)
	email: Mapped[str] = mapped_column(String(255) , unique = True , index = True)
	password_hash: Mapped[str] = mapped_column(String(255))
	
	notes: Mapped[list["Note"]] = relationship(back_populates = "owner")
	
class Note(Base):
	__tablename__ = "notes"
	
	id: Mapped[int] = mapped_column(primary_key = True)
	title: Mapped[str] = mapped_column(String(255))	
	body: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(default= lambda: datetime.now(timezone.utc))
	
	owner_id: Mapped[int] = mapped_column(ForeignKey("users.id") , index = True)
	owner: Mapped["User"] = relationship(back_populates = "notes")
