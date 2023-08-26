# -*- coding: utf-8 -*-
'''
Created on Sat 08 26 17:00:11 2023

@Author: Kingsley
'''
from datetime import datetime
from dateutil.relativedelta import relativedelta
from db_conn import RAW_DB
import  geopandas as gpd

# TODO 1.Time query
def construct_query_raw(adcode=None, year=None, month=None, filters=None, **kwargs):
    query = {}
    if year:
        year = int(year)
        if not month:
            start_time = datetime(year, 1, 1)
            end_time = start_time + relativedelta(years=1)
        else:
            month = int(month)
            start_time = datetime(year, month, 1)
            end_time = start_time + relativedelta(months=1)
        query['date_time'] = {'gte': start_time.isoformat(), '$lt': end_time.isoformat(),}
    if adcode:
        if type(adcode) == int:
            adcode = str(adcode)
        query["adcode"] = adcode
    if filters:
        query = {**query, **filters}
    if kwargs:
        query = {**query, **kwargs}
    return query


if __name__ == "__main__":
    my_query = construct_query_raw(adcode='110100')
    # print(gpd.GeoDataFrame.from_features(RAW_DB['2023_amap_boundary_city'].find(my_query)))
    print(list(RAW_DB['2023_amap_boundary_city'].find(my_query)))