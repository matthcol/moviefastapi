# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 00:34:35 2022

@author: Matthias
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dbmovie.db"
    database_test_url: str = "sqlite:///./dbmovietest.db"

    class Config:
        env_file = ".env"
