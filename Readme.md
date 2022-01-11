# API Rest movieapi with fastapi

## Configuration

Choose your db to run api or tests in .env file

## Install dependencies

### a. to run API only

pip(3) install -r requirements.txt

### b. to run tests

pip(3) install -r requirements-test.txt

### c. extra modules for other db

- pyscopg2 : postgresql
- pymysql : mysql ou mariadb

## Test api

pytest movieapi

## Run api

uvicorn movieapi.main:app --host 0.0.0.0 --port 8080