import pandas as pd
from db_conn import engine
from proj_utils.insert_postgres import insert_df



def init_city(adcode, conn=engine):
    """
    Initiate attribute table of house_price_city in rent
    :param adcode:
    :param conn:
    :return:
    """

    schema = 'transaction'
    table = 'house_price_city'

    sql_county = f"""
                    SELECT city.uid, city.adcode
                    FROM boundary.city AS city
                    WHERE city.adcode = {adcode}::text
    """
    county_df = pd.read_sql(sql_county, conn)
    county_df.rename(columns={'uid': 'city_uid'}, inplace=True)
    return insert_df(conn, county_df, table=table, schema=schema)


def init_county(adcode, conn=engine):
    """
    Initiate attribute table of house_price_county in rent
    :param adcode:
    :param conn:
    :return:
    """

    schema = 'transaction'
    table = 'house_price_county'

    sql_county = f"""
                    SELECT county.uid,county.adcode,county.city_adcode
                    FROM boundary.county AS county
                    WHERE county.city_adcode = {adcode}::text
    """
    county_df = pd.read_sql(sql_county, conn)
    county_df.rename(columns={'uid': 'county_uid'}, inplace=True)
    return insert_df(conn, county_df, table=table, schema=schema)
