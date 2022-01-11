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

@app.put("/api/movies/", response_model=schemas.Movie)
def update_movie(movie: schemas.Movie, db: Session = Depends(get_db)):
    db_movie = crud.update_movie(db, movie=movie)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie to update not found")
    return db_movie

@app.delete("/api/movies/{movie_id}", response_model=schemas.Movie)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.delete_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Item to delete not found")
    return db_movie

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

@app.get("/api/movies/byTitleYear", response_model=List[schemas.Movie])
def read_movies_by_title_year(t: str, y: int, db: Session = Depends(get_db)):
    return crud.get_movies_by_title_year(db=db, title=t, year=y)

@app.get("/api/movies/byYearRange", response_model=List[schemas.Movie])
def read_movies_by_year_range(ymi: Optional[int] = None, yma: Optional[int] = None, db: Session = Depends(get_db)):
    if ymi is not None and yma is not None:
        return crud.get_movies_by_year_range(db=db, year_min=ymi, year_max=yma)
    elif ymi is None and yma is not None:
        return crud.get_movies_by_year_max(db=db, year_max=yma)
    elif ymi is not None and yma is None:
        return crud.get_movies_by_year_min(db=db, year_min=ymi)
    else:
        raise HTTPException(status_code=405, detail="Selection by range not allowed without any year")
        
	
