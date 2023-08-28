# -*- coding: utf-8 -*-
"""
Created on 27 Aug 11:43 PM

@Author: kingsley leung
@Email: kingsleyl0107@gmail.com

_description_:
"""
from proj_utils.load_mongo_pro import construct_query_pro
import geopandas as gpd
from db_conn import Mongo_PRO, DATA_PRO
from proj_utils.insert_postgres import insert_df, gen_postgres_uid


def mongo_pro_boundary_province(year=2023, **kwargs):
    query = construct_query_pro(src="amap", cls="boundary_province", year=2023)
    total = Mongo_PRO.count_documents(query)
    print(f"total province num: {total}, query: {query}")
    provinces = gpd.GeoDataFrame.from_features(list(Mongo_PRO.find(query)), crs=4326)
    return provinces


def amap_province(year=2023):
    provinces = mongo_pro_boundary_province(2023)
    provinces2pg = provinces[['name', 'adcode', 'geometry']]
    insert_df(DATA_PRO, provinces2pg, table="province", schema="boundary", geotype='MULTIPOLYGON')


def mongo_pro_boundary_cities(year=2023, **kwargs):
    query = construct_query_pro(src="amap", cls="boundary_city", year=2023)
    total = Mongo_PRO.count_documents(query)
    print(f"total city num: {total}, query: {query}")
    cities = gpd.GeoDataFrame.from_features(list(Mongo_PRO.find(query)), crs=4326)
    return cities


def amap_city(year=2023):
    cities = mongo_pro_boundary_cities(2023)
    cities['province_adcode'] = cities['adcode'].astype(str).apply(lambda x: x[:2] + '0000').astype(int)
    cities2pg = cities[['name', 'adcode', "province_adcode", 'geometry']]
    insert_df(DATA_PRO, cities2pg, table="city", schema="boundary", geotype='MULTIPOLYGON')


if __name__ == "__main__":
    # amap_province(2023)
    amap_city(2023)
