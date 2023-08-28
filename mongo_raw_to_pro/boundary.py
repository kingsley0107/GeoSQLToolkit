# -*- coding: utf-8 -*-
"""
Created on 27 Aug 5:38 PM

@Author: kingsley leung
@Email: kingsleyl0107@gmail.com

_description_:
"""
from db_conn import RAW_DB, Mongo_PRO
from proj_utils.load_mongo_raw import construct_query_raw
from datetime import datetime


def process_province(year, **kwargs):
    query = construct_query_raw(**kwargs)
    boundaries = list(RAW_DB[f'{year}_amap_boundary_province'].find(query))
    for boundary in boundaries:
        data_into_pro = {}
        data_into_pro['source'] = 'amap'
        data_into_pro['class'] = "boundary_province"
        data_into_pro['adcode'] = boundary['properties']['adcode']
        data_into_pro['properties'], data_into_pro['geometry'] = boundary['properties'], boundary['geometry']
        data_into_pro['date_time'] = datetime.now()
        Mongo_PRO.insert_one(data_into_pro)
        print(f"inserted {data_into_pro['properties']['name']}")


def process_city(year, **kwargs):
    query = construct_query_raw(**kwargs)
    boundaries = list(RAW_DB[f'{year}_amap_boundary_city'].find(query))
    for boundary in boundaries:
        data_into_pro = {}
        data_into_pro['properties'], data_into_pro['geometry'] = boundary['properties'], boundary['geometry']
        data_into_pro['source'] = 'amap'
        data_into_pro['class'] = "boundary_city"
        data_into_pro['adcode'] = boundary['properties']['adcode']
        data_into_pro['date_time'] = datetime.now()
        Mongo_PRO.insert_one(data_into_pro)
        print(f"inserted {data_into_pro['properties']['name']}")

if __name__ == "__main__":
    process_province(2023)
    process_city(2023)
