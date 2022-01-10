"""
database.py : config orm
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./dbmovie.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://movie:password@localhost:5432/dbmovie"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://movie:password@localhost/dbmovie"
# SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://movie:password@localhost/dbmovie"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},   # only for SQLITE
    echo=True       # to see SQL queries in logs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
  