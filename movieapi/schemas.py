"""
schema.py : model to be converted in json by fastapi
"""
from typing import Optional
from datetime import date

from pydantic import BaseModel



# common Base Class for Movies (abstract class)
class MovieBase(BaseModel):
    title: str
    year: int
    duration: Optional[int]
    synopsis: Optional[str]
    posterUri: Optional[str]

# movies witout id, only for creation purpose
class MovieCreate(MovieBase):
    pass

# movies from database with id
class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True

    
        
