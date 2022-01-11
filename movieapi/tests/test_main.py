# -*- coding: utf-8 -*-
"""
e2e tests for the movieapi

Created on Mon Jan 10 23:44:51 2022

@author: Matthias
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db
from ..config import Settings

settings = Settings()

SQLALCHEMY_DATABASE_URL = settings.database_test_url

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},   # only for SQLITE
        echo=True       # to see SQL queries in logs
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        echo=True       # to see SQL queries in logs
    )
    
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

# override db conf from main api
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# create database before ech test, dropt it after
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_movie(test_db):
    # facts
    title =  "Nobody"
    year = 2021
    # when
    response = client.post(
        "/api/movies/",
        json={"title": title, "year": year},
    )
    # then
    # check response
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == title
    assert "id" in data
    movie_id = data["id"]

    # check again by reading the data again 
    response = client.get(f"/api/movies/byId/{movie_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == title
    assert data["year"] == year
    assert data["id"] == movie_id
    
    
def test_update_movie(test_db):
    # facts
    title =  "Nobod"
    year = 2020
    # when
    response = client.post(
        "/api/movies/",
        json={"title": title, "year": year},
    )
    assert response.status_code == 200, response.text
    movie_posted = response.json()
    movie_id = movie_posted["id"]
    # new facts
    title2 =  "Nobody"
    year2 = 2021
    duration2 = 92
    synopsis2 = "Emmy winner Bob Odenkirk (Better Call Saul, The Post, Nebraska) stars as Hutch Mansell, an underestimated and overlooked dad and husband, taking life's indignities on the chin and never pushing back. A nobody. When two thieves break into his suburban home one night, Hutch declines to defend himself or his family, hoping to prevent serious violence. His teenage son, Blake (Gage Munroe, The Shack), is disappointed in him and his wife, Becca (Connie Nielsen, Wonder Woman), seems to pull only further away. The aftermath of the incident strikes a match to Hutch's long-simmering rage, triggering dormant instincts and propelling him on a brutal path that will surface dark secrets and lethal skills. In a barrage of fists, gunfire and squealing tires, Hutch must save his family from a dangerous adversary (famed Russian actor Aleksey Serebryakov, Amazon's McMafia)-and ensure that he will never be underestimated as a nobody again."
    posterUri2 = "https://m.media-amazon.com/images/M/MV5BMjM5YTRlZmUtZGVmYi00ZjE2LWIyNzAtOWVhMDk1MDdkYzhjXkEyXkFqcGdeQXVyMjMxOTE0ODA@._V1_FMjpg_UY759_.jpg"
    # when
    response = client.put(
        "/api/movies/",
        json={
            "id": movie_id,
            "title": title2, 
            "year": year2,
            "duration":duration2,
            "synopsis": synopsis2,
            "posterUri": posterUri2
        })
    # then
    # check response
    assert response.status_code == 200, response.text
    movie_updated = response.json()
    assert movie_updated["id"] == movie_id
    assert movie_updated["title"] == title2
    assert movie_updated["year"] == year2
    assert movie_updated["duration"] == duration2
    assert movie_updated["synopsis"] == synopsis2
    assert movie_updated["posterUri"] == posterUri2
    
    # # check again
    response = client.get(f"/api/movies/byId/{movie_id}")
    assert response.status_code == 200, response.text
    movie_read = response.json()
    assert movie_read["id"] == movie_id
    assert movie_updated["title"] == title2
    assert movie_read["year"] == year2
    assert movie_read["duration"] == duration2
    assert movie_read["synopsis"] == synopsis2
    assert movie_read["posterUri"] == posterUri2
        
def test_delete_movie(test_db):
    # facts
    title =  "Nobody"
    year = 2021
    
    # post facts
    response = client.post(
        "/api/movies/",
        json={"title": title, "year": year},
    )
    assert response.status_code == 200, response.text
    movie_posted = response.json()
    movie_id = movie_posted["id"]
    
    # when
    response = client.delete(
        f"/api/movies/{movie_id}")
    # then
    # check response
    assert response.status_code == 200, response.text
    movie_deleted = response.json()
    assert movie_deleted["id"] == movie_id
    assert movie_deleted["title"] == title
    assert movie_deleted["year"] == year
    
    # check again
    response = client.get(f"/api/movies/byId/{movie_id}")
    assert response.status_code == 404
    
    # delete previuously removed movie
    response = client.delete(
        f"/api/movies/{movie_id}")
    assert response.status_code == 404
    
    
@pytest.fixture()
def init_data(test_db):
    data_posted = [ 
        client.post("/api/movies/", json={"title": "Nobody", "year": 2021}).json(),
        client.post("/api/movies/", json={"title": "Black Widow", "year": 2021}).json(),
        client.post("/api/movies/", json={"title": "No Time To Die", "year": 2021}).json(),
        client.post("/api/movies/", json={"title": "The Man Who Knew Too Much", "year": 1934}).json(),
        client.post("/api/movies/", json={"title": "The Man Who Knew Too Much", "year": 1956}).json(),
        client.post("/api/movies/", json={"title": "Spectre", "year": 2015}).json(),
        client.post("/api/movies/", json={"title": "Casino Royale", "year": 2006}).json(),
        client.post("/api/movies/", json={"title": "Skyfall", "year": 2012}).json(),
    ]
    return data_posted
    

def test_read_movies(init_data):
    response = client.get("/api/movies/")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    assert len(movies_read) == 8
    assert min(m["year"] for m in movies_read) == 1934
    assert max(m["year"] for m in movies_read) == 2021
    titles = [ m["title"] for m in movies_read ]
    assert len([t for t in titles if t == "The Man Who Knew Too Much"]) == 2
    assert "Nobody" in titles
    assert "Black Widow" in titles
    assert "No Time To Die" in titles
    assert "Spectre" in titles
    assert "Casino Royale" in titles
    assert "Skyfall" in titles
    

def test_read_movie(init_data):
    first_movie = init_data[0]
    movie_id = first_movie["id"]
    # read first movie by its id
    response = client.get(f"/api/movies/byId/{movie_id}")
    assert response.status_code == 200, response.text
    movie_read = response.json()
    # then
    assert movie_read["id"] == first_movie["id"]
    assert movie_read["title"] == first_movie["title"]
    assert movie_read["year"] == first_movie["year"]
    # read absent id
    movie_id = max(m["id"] for m in init_data) + 1
    response = client.get(f"/api/movies/byId/{movie_id}")
    assert response.status_code == 404    


def test_read_movies_by_title(init_data):
    title = "The Man Who Knew Too Much"
    response = client.get(f"/api/movies/byTitle?t={title}")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    # then
    assert len(movies_read) == 2
    for m in movies_read:
        assert m["title"] == title
    
def test_read_movies_by_title_year(init_data):
    title = "The Man Who Knew Too Much"
    year = 1956
    response = client.get(f"/api/movies/byTitleYear?t={title}&y={year}")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    assert len(movies_read) == 1
    movie_read = movies_read[0]
    assert movie_read["title"] == title
    assert movie_read["year"] == year
    
def test_read_movies_by_year_range_1YearMin(init_data):
    yearMax = 2020
    # when 
    response = client.get(f"/api/movies/byYearRange?ymi={yearMax}")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    # then 
    assert all(((m["year"] >= yearMax) for m in movies_read))
    assert len(movies_read) == 3
    titles = [ m["title"] for m in movies_read ]
    assert "Nobody" in titles
    assert "Black Widow" in titles
    assert "No Time To Die" in titles

def test_read_movies_by_year_range_2Years(init_data):
    yearMin = 1950
    yearMax = 2020    
    # when 
    response = client.get(f"/api/movies/byYearRange?ymi={yearMin}&yma={yearMax}")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    # then 
    assert all(((yearMin <= m["year"] <= yearMax) for m in movies_read))
    assert len(movies_read) == 4
    titles = [ m["title"] for m in movies_read ]
    assert "Spectre" in titles
    assert "Casino Royale" in titles
    assert "Skyfall" in titles
    assert "The Man Who Knew Too Much" in titles

def test_read_movies_by_year_range_1YMax(init_data):
    yearMin = 1950
    # when 
    response = client.get(f"/api/movies/byYearRange?yma={yearMin}")
    assert response.status_code == 200, response.text
    movies_read = response.json()
    # then 
    assert all(((m["year"] <= yearMin) for m in movies_read))
    assert len(movies_read) == 1
    assert movies_read[0]["title"] == "The Man Who Knew Too Much"
    
def test_read_movies_by_year_range_NoYear(init_data):
    # when 
    response = client.get("/api/movies/byYearRange")
    # then : not allowed
    assert response.status_code == 405, response.text
    
    