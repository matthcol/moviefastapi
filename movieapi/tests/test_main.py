# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 23:44:51 2022

@author: Matthias
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./dbmovietest.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_movie():
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
