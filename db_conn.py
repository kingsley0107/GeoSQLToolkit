from sqlalchemy import create_engine
from enum import Enum
from pymongo import MongoClient


class PGConfigs(str, Enum):
    HOST = 'localhost'
    PORT = '5432'
    Database = 'GeoSQLToolkit'
    User = 'postgres'
    Password = '545591917'


# 连接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
RAW_DB = client["GeoSQLToolkit"]


engine = create_engine(
    f"postgresql://{PGConfigs.User}:{PGConfigs.Password}@{PGConfigs.HOST}:{PGConfigs.PORT}/{PGConfigs.Database}")
