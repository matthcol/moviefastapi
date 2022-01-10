"""
model.py : database row <-> objet python
"""
from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.orm import relationship

from .database import Base



class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=250), nullable=False)
    year = Column(SmallInteger, nullable=False)
    duration = Column(SmallInteger, nullable=True)
    synopsis = Column(String(length=4000), nullable=True)
    posterUri = Column(String(length=500), nullable=True)
