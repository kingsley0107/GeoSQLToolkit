# -*- coding: utf-8 -*-
"""
Created on 25 Aug 10:44 AM

@Author: kingsley leung
@Email: kingsleyl0107@gmail.com

_description_:
"""
import pandas as pd
import geopandas as gpd
import requests
import json
import time
import datetime
from shapely.geometry import Polygon, MultiPolygon
from db_conn import RAW_DB, engine
import re

class BoundariesCrawler:
    def __init__(self, level):
        self.base_url = "https://restapi.amap.com/v3/config/district?"
        self.amap_key = "aaf04443bb4dc7e3c0edc365fe5e7f83"
        self.level = level
        self._user_SessionConfig()

    def _user_SessionConfig(self):
        self.cookie = """cna=D2t3G7QczToCAd9KTy8b7FaR; passport_login=NjAxOTI4MTQ5LGFtYXBfMTM3MTM5NDAzODBBRzJrdFl3bE0seW5nYTM0b21xeXhja2dkc3BhNXZtYXduYXNuZGZjd3osMTY5MTY1MTE4MixNek5tWVdWbFlXRTBPVFV3WWpkaFpUTXdOamt4WkdJMFkyVTJaVGN6WXpNPQ%3D%3D; xlly_s=1; gray_auth=2; l=fBQLz3jHTBMvGKPyBOfaFurza77OSIRYYuPzaNbMi9fP_YCB5hScW1t97LY6C3GNF62eR3-WjmOpBeYBqQAonxv9lN9agSkmndLHR35..; isg=BGRk05q23D_oSy8zAw3vJjFTNWJW_Yhn0i8SAH6FMy_yKQXzpgxq9Yub74kx6sC_; tfstk=dXnwRVMwEhKwwnamozrqUxmUrzrTDud5omNbnxD0C5ViGEFm8jGeBSMD6jo4tjPjClj10rkma-_j5CIqTbDrCm9Tjokm1WnjC5NbonlmEjzvBSN0gjMm5ptWVAHTDoV2N3t5YxqYmroAihDtBoEDNQtWVAeV6r6AnASmmVyMkk6pJjMtYRzMPAVhmJnUQPPoIZscQZ1YK-bsDV5cuP2LL79eLAC4PUf.."""
        self.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        self.host = "restapi.amap.com"
        self.headers = {
            "User-Agent": self.UserAgent,
            "Cookie": self.cookie,
            "Host": self.host
        }

    def get_province_list(self):
        provinces = ['北京市', '重庆市', '天津市', '上海市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省',
                     '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省', '湖北省',
                     '湖南省', '广东省', '广西壮族自治区', '海南省', '四川省', '贵州省', '云南省', '西藏自治区',
                     '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区', '台湾省', '香港特别行政区',
                     '澳门特别行政区']
        return provinces

    def get_cities_list(self):
        cities_info = pd.read_csv(r'./mainland_adcode.csv')
        cities_list = cities_info['NAME'].values.tolist()
        return cities_list

    def request_url(self, url, params=None):
        """通用request请求器

        Args:
            url (_type_): _待爬url_
            params (_type_, optional): _params_. Defaults to None.

        Returns:
            _type_: _description_
        """
        response = requests.get(url=url, params=params, headers=self.headers)
        return json.loads(response.text)

    def extract_gdf(self, raw_data):
        if raw_data['districts'][0]['level'] != self.level:
            raise TypeError("administration level is not match.")
        _this = raw_data['districts'][0]
        _this_name, _this_adcode, _this_level = _this['name'], _this['adcode'], _this['level']

        _this_geom = list(map(
            lambda pair: tuple(map(float, pair.split(","))),
            re.split(r'[;|]', _this['polyline'])
        ))
        multi_polygon = MultiPolygon([Polygon(_this_geom)])
        gdf = gpd.GeoDataFrame(
            {'name': [_this_name], "adcode": [_this_adcode], "level": [_this_level], "geometry": [multi_polygon]},
            geometry='geometry'
        )
        data_to_mongo = gdf.iloc[0].to_dict()
        data_to_mongo['geometry'] = data_to_mongo['geometry'].__geo_interface__

        return data_to_mongo

    def crawl_boundaries(self):
        params = {
            "keywords": None,
            "subdistrict": 0,
            "extensions": 'all',
            "key": self.amap_key
        }
        print(f"Start crawling {self.level} from AMap...")
        if self.level == 'city':
            administration_list = self.get_cities_list()
        elif self.level == 'province':
            administration_list = self.get_province_list()
        for district in administration_list:
            params['keywords'] = district
            request_response = self.request_url(self.base_url, params=params)
            data_to_mongo = self.extract_gdf(request_response)
            self.data_to_mongo(data_to_mongo)

    def data_to_mongo(self, row_data):
        current_year = datetime.datetime.now().year
        collection_name = f'{current_year}_amap_boundary_{self.level}'

        # 查询集合中是否已存在相同省份的记录
        existing_record = RAW_DB[collection_name].find_one({"name": row_data['name']})

        if existing_record is None:
            RAW_DB[collection_name].insert_one(row_data)
            print(f"Inserted {row_data['name']}...")
        else:
            print(f"Skipped insertion for {row_data['name']} (already exists)...")


if __name__ == "__main__":
    start_time = time.time()
    BoundariesCrawler("province").crawl_boundaries()
    print("--- %s seconds ---" % (time.time() - start_time))
