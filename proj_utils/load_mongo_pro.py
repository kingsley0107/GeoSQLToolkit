# -*- coding: utf-8 -*-
"""
Created on 28 Aug 11:27 PM

@Author: kingsley leung
@Email: kingsleyl0107@gmail.com

_description_:
"""
from datetime import datetime
from db_conn import Mongo_PRO

def construct_query_pro(
        src=None, cls=None, year=None, adcode=None, month=None, filters=None, **kwargs
):
    query = {}
    if src:
        query["source"] = src
    if cls:
        query["class"] = cls
    if year:
        year = int(year)
        if month is None:
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
        else:
            month = int(month)
            start = datetime(year, month, 1)
            end = datetime(year, month + 1, 1)
        query["date_time"] = {"$gte": start, "$lt": end}
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
    list(Mongo_PRO.find(construct_query_pro(src="amap", cls="boundary_province", year=2023)))
