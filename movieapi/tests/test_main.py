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
    
