from db_conn import engine
from proj_utils.zero2null import *
from proj_utils.filter import filter_date


def shop_office_rent_update(adcode, start_year, start_month, end_year, end_month, rent_type, conn=engine):
    """
    Calculate avg daily unit rent for each grid
    :param rent_type: 'shop' or 'office'
    """
    start_day = f'{start_year}-{start_month}-01'
    if end_month == 12:
        end_month = 1
        end_year = end_year + 1
    end_day_plus1 = f'{end_year}-{end_month + 1}-01 '

    sql1 = f"""
    WITH dailyrent as (
        SELECT SUM(total_rent)/SUM(area)/30 unitrent, grid.uid grid_uid, max(rent.date_time) max_dt
        FROM transaction.lj_{rent_type}_rent rent, grid.grid_200 grid
        WHERE ST_CONTAINS(grid.geometry, rent.geometry)
        AND rent.adcode = {adcode}::text
        AND {filter_date('rent', start_day, end_day_plus1)}
        AND grid.adcode = {adcode}::text
        GROUP BY grid.uid
    )
    UPDATE grid.transaction trans
    SET {rent_type}_rent = round(dailyrent.unitrent::numeric, 2),
        date_time = dailyrent.max_dt
    FROM dailyrent
    WHERE trans.grid_uid = dailyrent.grid_uid;
    """
    with conn.begin() as con:
        con.connect().execute(sql1)


def resi_rent_price_area_update(adcode, start_year, start_month, end_year, end_month, conn=engine):
    """
    Calculate avg residence unit rent price and avg residence rent area for each grid
    """
    start_day = f'{start_year}-{start_month}-01'
    if end_month == 12:
        end_month = 1
        end_year = end_year + 1
    end_day_plus1 = f'{end_year}-{end_month + 1}-01 '
    sql1 = f"""
    WITH rent as (
        SELECT SUM(total_rent)/SUM(area) unitrent, SUM(area)/COUNT(rent.uid) avg_area, grid.uid grid_uid, max(rent.date_time) max_dt
        FROM transaction.lj_resi_rent rent, grid.grid_200 grid
        WHERE ST_CONTAINS(grid.geometry,rent.geometry)
        AND rent.adcode = {adcode}::text
        AND {filter_date('rent', start_day, end_day_plus1)}
        AND grid.adcode = {adcode}::text
        GROUP BY grid.uid
    )
    UPDATE grid.transaction trans
    SET residence_rent_price = round(rent.unitrent::numeric, 2),
        rent_residence_area = round(rent.avg_area::numeric, 2),
        date_time = rent.max_dt
    FROM rent
    WHERE trans.grid_uid = rent.grid_uid;
    """
    with conn.begin() as con:
        con.connect().execute(sql1)


def resi_sale_price_update(adcode, start_year, start_month, end_year, end_month, conn=engine):
    """
    Calculate avg unit sale price for each grid
    """
    start_day = f'{start_year}-{start_month}-01'
    if end_month == 12:
        end_month = 1
        end_year = end_year + 1
    end_day_plus1 = f'{end_year}-{end_month + 1}-01 '
    sql1 = f"""
    WITH sale as (
        SELECT SUM(total_price)/SUM(area) unitprice, grid.uid grid_uid, max(sale.date_time) max_dt
        FROM transaction.lj_second_resi_sale sale, grid.grid_200 grid
        WHERE ST_CONTAINS(grid.geometry, sale.geometry)
        AND sale.adcode = {adcode}::text
        AND {filter_date('sale', start_day, end_day_plus1)}
        AND grid.adcode = {adcode}::text
        GROUP BY grid.uid
    )
    UPDATE grid.transaction trans
    SET residence_sale_price = round(sale.unitprice::numeric, 2),
        date_time = sale.max_dt
    FROM sale
    WHERE trans.grid_uid = sale.grid_uid;

    """
    with conn.begin() as con:
        con.connect().execute(sql1)

