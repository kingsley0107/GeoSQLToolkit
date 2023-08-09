import random

import geopandas as gpd
from amap_poi_crawl import AmapPoi


def core_area(adcode):
    # Builtup area
    bd = get_gdf(cls='builtup_area', adcode=adcode)
    to_mercator(bd)
    bd.geometry = bd.geometry.buffer(500)
    bd.to_crs(4326, inplace=True)
    return bd


# -------------------------------- All ----------------------------------

typecodes_lst = [
    ['060000'],
    ['050000',
     '120100',
     '120203',
     '120300',
     '140400',
     '140200',
     '140400',
     '140500',
     '140600',
     '140700',
     '140800',
     '140900',
     '141000',
     '141200',
     '141300',
     ],
    ['070400',
     '070500',
     '071100',
     '071300',
     '071500',
     '072000',
     '150100',
     '150200',
     '150300',
     '150400',
     '150900',
     '160100',
     '160400',
     '160500',
     '160600',
     '170000',
     '200300'
     ],
    ['010100',
     '010200',
     '010300',
     '011100',
     '080000',
     '090100',
     '090200',
     '090300',
     '090601',
     '110000',
     '130000',
     ]
]
tpcd_str = ['|'.join(t) for t in typecodes_lst]

for adcode in target_cities:
    bd = core_area(adcode)
    producer = AmapPoiUrlProducer(
        adcode, resolution=0.02, city_boundary=bd, typecode_strs=tpcd_str)
    producer.poi_by_city()
