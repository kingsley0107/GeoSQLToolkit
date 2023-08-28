# -*- coding: utf-8 -*-
"""
Created on 28 Aug 11:17 PM

@Author: kingsley leung
@Email: kingsleyl0107@gmail.com

_description_:
"""
import numpy as np
import pandas as pd
import string
import random
from datetime import datetime
from pandas.api.types import is_datetime64_any_dtype
from shapely.geometry import mapping
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy.exc import IntegrityError


def gen_rand_str(l=5):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(l))


def hex_hash(to_hash):
    return hex(hash(str(to_hash)))


def gen_postgres_uid(hash_obj=None):
    # for fields that gen same uid
    if hash_obj:
        hash_hex = hex_hash(hash_obj)

        rand = gen_rand_str(6)
    else:
        hash_hex = ''

        # Random str
        rand = gen_rand_str(24)

    return rand + hash_hex


def insert_df(conn, df: pd.DataFrame, table: str, schema: str, uid_hash_col=None,
              geotype: str = 'GEOMETRY', srid=4326):
    """
    naive insert to PostgresDB
    :param conn: SQLAlchemy's engine
    :param df: default format for `date_time` column is "%Y-%m-%dT%H:%M:%SZ"
    :param geotype: possible values: "GEOMETRY", "POINT", "LINESTRING", "POLYGON",
     "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON", "GEOMETRYCOLLECTION", "CURVE",
    :param uid_hash_col: column to hash in uid
    :return:
    """
    # Format date_time column
    if "date_time" not in df.columns:
        # Add current time as date_time
        df['date_time'] = datetime.now()
    else:
        if not is_datetime64_any_dtype(df['date_time']):
            # Try to convert date_time from string to datetime, default format is "%Y-%m-%dT%H:%M:%SZ"
            df['date_time'] = df['date_time'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%dT%H:%M:%SZ"))

    # Generate UID
    if 'uid' in df.columns:
        print('uid in df columns, skip generating uid!')
    else:
        if uid_hash_col:
            if uid_hash_col == 'geometry':
                df['uid'] = df['geometry'].apply(lambda x: gen_postgres_uid(mapping(x)))
            else:
                df['uid'] = df[uid_hash_col].apply(lambda x: gen_postgres_uid(x))
        else:
            if 'geometry' in df.columns:
                df['uid'] = df['geometry'].apply(lambda x: gen_postgres_uid(mapping(x)))
            else:
                df['uid'] = df[df.columns[0]].apply(lambda x: gen_postgres_uid())

    # Format geometry
    if 'geometry' in df.columns:
        df['geometry'] = df['geometry'].apply(lambda x: WKTElement(x.wkt, srid=srid))

        # Use 'dtype' to specify column's type
        # For the geom column, we will use GeoAlchemy's type 'Geometry'
        return df_to_sql(df, name=table, con=conn, schema=schema, if_exists='append',
                         index=False, dtype={'geometry': Geometry(geotype, srid=srid)})
    else:
        return df_to_sql(df, name=table, con=conn, schema=schema, if_exists='append', index=False)


def df_to_sql(df, name, con, schema, if_exists='append', index=False, **kwagrs):
    """Ignore invalid row"""
    try:
        return df.to_sql(name=name, con=con, schema=schema, if_exists=if_exists, index=index, **kwagrs)
    except IntegrityError as e:
        # print(e, ' try split df')
        print(f'IntegrityError, split df of size {df.size}')
        df1, df2 = _split_df(df)
        df_to_sql(df1, name, con, schema, if_exists, index, **kwagrs)
        df_to_sql(df2, name, con, schema, if_exists, index, **kwagrs)


def _split_df(df):
    if len(df) % 2 != 0:  # Handling `df` with `odd` number of rows
        df = df.iloc[:-1, :]
    df1, df2 = np.array_split(df, 2)
    return df1, df2
