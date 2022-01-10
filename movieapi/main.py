"""
    
"""
from typing import List, Optional, Tuple
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.logger import logger as fastapi_logger
from sqlalchemy.orm import Session

import movieapi.crud as crud
import movieapi.models as models
import movieapi.schemas as schemas
from .database import SessionLocal, engine

# generate auo ddl in mode update
models.Base.metadata.create_all(bind=engine)


app = FastAPI()

logger = logging.getLogger("uvicorn")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)
logger.error("API Started")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/movies/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db=db, movie=movie)


@app.get("/api/movies/", response_model=List[schemas.Movie])
def read_movies(skip: Optional[int] = 0, limit: Optional[int] = 100, db: Session = Depends(get_db)):
    # read movies from database
    movies = crud.get_movies(db, skip=skip, limit=limit)
    # return them as json
    return movies

@app.get("/api/movies/byId/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie to read not found")
    return db_movie

@app.get("/api/movies/byTitle", response_model=List[schemas.Movie])
def read_movies_by_title(t: str, db: Session = Depends(get_db)):
    return crud.get_movies_by_title_part(db=db, title=t)