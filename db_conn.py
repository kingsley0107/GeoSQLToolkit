from sqlalchemy import create_engine
from enum import Enum
from pymongo import MongoClient


class PGConfigs(str, Enum):
    HOST = 'localhost'
    PORT = '5432'
    Database = 'GeoSQLToolkit'
    User = 'postgres'
    Password = '545591917'


# For MongoDB to store raw data
client = MongoClient("mongodb://localhost:27017/")
RAW_DB = client["GeoSQLToolkit"]

# For MongoDB to store pro-data
Mongo_PRO = client['DATA_PRO']['data_production']


# For PGSQL to store product data
DATA_PRO = create_engine(
    f"postgresql://{PGConfigs.User}:{PGConfigs.Password}@{PGConfigs.HOST}:{PGConfigs.PORT}/{PGConfigs.Database}")
