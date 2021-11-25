"""
file crud.py
manage CRUD and adapt model data from db to schema data to api rest
"""

from typing import Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, extract, between, distinct
from sqlalchemy import func
from fastapi.logger import logger
import models, schemas

# CRUD for Movie objects
def get_movie(db: Session, movie_id: int):
    # read from the database (get method read from cache)
    # return object read or None if not found
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    logger.error(f"Movie retrieved from DB: {db_movie.title}")
    logger.error("director: {}".format( 
              db_movie.director.name if db_movie.director is not None else "no director"))
    logger.error(f"actors: {db_movie.actors}")
    return db_movie;

def get_movies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movie).offset(skip).limit(limit).all()

def _get_movies_by_predicate(*predicate, db: Session):
    """ partial request to apply one or more predicate(s) to model Movie"""
    return db.query(models.Movie)   \
            .filter(*predicate)

def get_movies_by_title(db: Session, title: str):
    return _get_movies_by_predicate(models.Movie.title == title, db=db)    \
            .order_by(desc(models.Movie.year))                      \
            .all()
            
def get_movies_by_title_part(db: Session, title: str):
    return _get_movies_by_predicate(models.Movie.title.like(f'%{title}%'), db=db)   \
            .order_by(models.Movie.title, models.Movie.year)                       \
            .all()

def get_movies_by_year(db: Session, year: int):
    return _get_movies_by_predicate(models.Movie.year == year, db=db)    \
            .order_by(models.Movie.title)                         \
            .all()

def get_movies_by_range_year(db: Session, year_min: Optional[int], year_max: Optional[int]):
    if year_min is None and year_max is None:
        return None
    if year_min is None:
        predicate = models.Movie.year <= year_max
    elif year_max is None:
        predicate = models.Movie.year >= year_min
    else:
        predicate = between(models.Movie.year, year_min, year_max)
    return _get_movies_by_predicate(predicate, db=db)                  \
            .order_by(models.Movie.year, models.Movie.title)    \
            .all()

def get_movies_by_title_year(db: Session, title: str, year: int):
    return _get_movies_by_predicate(
                    models.Movie.title == title, 
                    models.Movie.year == year,
                    db=db)                                      \
            .order_by(models.Movie.year, models.Movie.title)    \
            .all()

def get_movies_count(db: Session):
    return db.query(models.Movie).count()

def get_movies_count_year(db: Session, year: int):
    return _get_movies_by_predicate(models.Movie.year == year).count()

def get_movies_by_director_endname(db: Session, endname: str):
    return db.query(models.Movie).join(models.Movie.director)      \
            .filter(models.Star.name.like(f'%{endname}')) \
            .order_by(desc(models.Movie.year))  \
            .all()

def get_movies_by_actor_endname(db: Session, endname: str):
    return db.query(models.Movie).join(models.Movie.actors) \
            .filter(models.Star.name.like(f'%{endname}'))   \
            .order_by(desc(models.Movie.year))              \
            .all()
            
def get_movies_count_by_year(db: Session):
    # NB: func.count() i.e. count(*) en SQL
    return db.query(models.Movie.year, func.count())  \
            .group_by(models.Movie.year)  \
            .order_by(models.Movie.year)  \
            .all()

# alt. version returning dict instead of tuple
def get_stats_movies_by_year_dict(db: Session):
    query = db.query(models.Movie.year, 
                    func.count().label("movie_count"),
                    func.min(models.Movie.duration).label("min_duration"),
                    func.max(models.Movie.duration).label("max_duration"),
                    func.avg(models.Movie.duration).label("avg_duration"))  \
        .group_by(models.Movie.year)     \
        .order_by(models.Movie.year)   
    return [ {'year':y, 'movie_count': mc, 'min_duration': mid, 'max_duration': mxd, 'avg_duration': ad} 
            for y,mc,mid,mxd,ad in query ]

# CRUD association

def update_movie_director(db: Session, movie_id: int, director_id: int):
    db_movie = get_movie(db=db, movie_id=movie_id)
    db_star =  get_star(db=db, star_id=director_id)
    if db_movie is None or db_star is None:
        return None
    # update object association
    db_movie.director = db_star
    # commit transaction : update SQL
    db.commit()
    # return updated object
    return db_movie

# CRUD for Star objects
def _get_stars_by_predicate(*predicate, db: Session):
    """ partial request to apply one or more predicate(s) to model Star"""
    return db.query(models.Star)   \
            .filter(*predicate)    

def get_star(db: Session, star_id: int):
    # read from the database (get method read from cache)
    # return object read or None if not found
    return db.query(models.Star).filter(models.Star.id == star_id).first()
    #return db.query(models.Star).get(1)
    #return schemas.Star(id=1, name="Fred")

def get_stars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Star).offset(skip).limit(limit).all()

def get_stars_by_name(db: Session, name: str):
    return _get_stars_by_predicate(models.Star.name == name, db=db) \
            .order_by(models.Star.birthdate)  \
            .all()

def get_stars_by_endname(db: Session, name: str):
    return _get_stars_by_predicate(models.Star.name.like(f'%{name}'), db=db) \
            .order_by(models.Star.birthdate)  \
            .all()

def get_stars_by_birthyear(db: Session, year: int):
    return _get_stars_by_predicate(extract('year', models.Star.birthdate) == year, db=db) \
            .order_by(models.Star.name)  \
            .all()

def get_stars_count(db: Session):
    return db.query(models.Star).count()

def get_star_director_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id)  \
        .join(models.Movie.director).first()
    if db_movie is not None:
        return db_movie.director
    else:
        return None
    
def get_star_director_movie_by_title(db: Session, title: str):
    db_movies = db.query(models.Movie).filter(models.Movie.title.like(f'%{title}%')) \
        .join(models.Movie.director)  
    return [ db_movie.director for db_movie in db_movies ]

def get_stats_movie_by_director(db: Session, min_count: int):
    return db.query(models.Star, func.count(models.Movie.id).label("movie_count"))  \
        .join(models.Movie.director)        \
        .group_by(models.Star)  \
        .having(func.count(models.Movie.id) >= min_count) \
        .order_by(desc("movie_count")) \
        .all()
        
def get_stats_by_actor_director(db: Session,mina: int, mind: int):
    movie_a = aliased(models.Movie, name='movie_a')
    movie_d = aliased(models.Movie, name='movie_d')
    stars_a = aliased(models.Star, name='stars_a')
    stars_d = aliased(models.Star, name='stars_d')

    actors = db.query(movie_a.actors, 
                func.count(distinct(movie_a.id)).label('count_a'), 
                func.min(movie_a.year).label('min_year_a'), 
                func.max(movie_a.year).label('max_year_a'))\
        .join(movie_a.actors)\
        .group_by(movie_a.actors).all()
        #\.subquery()
    # directors = db.query(stars_d, 
    #             func.count(distinct(movie_d.id)).label('count_d'), 
    #             func.min(movie_d.year).label('min_year_d'), 
    #             func.max(movie_d.year).label('max_year_d'))\
    #     .join(movie_d.director)\
    #     .group_by(stars_d)\
    #     .subquery(name='d')
    # return actors.join(directors, movie_a.dircor == directors.columns.id).all()
    return actors 
        #.join(movie_d.director, isouter=True)\
        #.having(func.count(models.Movie.id) >= min_count)\
        #.order_by(desc(func.count(models.Movie.id)))\


# exemple of alias
#        actor = db.query(models.Stars).alias("actor")
#        director = db.query(models.Movies).alias("director")
#        actor.join(models.Movie.actors)
#        ....    
#        .join(director)





