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
    
