import os
from datetime import datetime
import pymongo

ROOT = os.path.dirname(os.path.realpath(__file__))
# mongoDB
# Raw data mongodb
if os.environ.get('POSITION') == 'INTER_NODE':
    HOSTNAME = 'XXX'
else:
    HOSTNAME = 'XXX'
PORT = 3717
USERNAME = 'scrapy_mongo_rw'
PASSWORD = 'XXX'
MONGODB_NAME = 'scrapy_mongo'
MONGO_URI = f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/?authSource={MONGODB_NAME}&authMechanism=SCRAM-SHA-1'
RAW_DB = pymongo.MongoClient(MONGO_URI)['scrapy_mongo']

MONGO_IN_COLL = '0_tiles_'
YEAR = str(datetime.now().year)
SOURCE = 'amap'
