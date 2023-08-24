from sqlalchemy import create_engine
from enum import Enum

class PGConfigs(str,Enum):
    HOST = 'localhost'
    PORT = '5432'
    Database = 'GeoSQLToolkit'
    User = 'postgres'
    Password = '545591917'


engine = create_engine(f"postgresql://{PGConfigs.User}:{PGConfigs.Password}@{PGConfigs.HOST}:{PGConfigs.PORT}/{PGConfigs.Database}")