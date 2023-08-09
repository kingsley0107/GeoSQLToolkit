# -*- coding: utf-8 -*-
'''
edited on  18:31:39, 09/08 2023

@Author  :   kingsley
@Email :   kingsleyl0107@gmail.com
'''

import traceback

import requests
import time
from datetime import date, datetime
import random

import numpy as np
from shapely.geometry import Point

from geo_utils.transcoords import gcj02towgs84


def comma_replace(text):
    if text:
        return text.replace(',', ';').strip()
    else:
        return 'null'


def str_6d(num):
    return format(num, '.6f')


def coords2bound(lngmax, latmin, lngmin, latmax):
    bound = '{},{}|{},{}'.format(str_6d(lngmax), str_6d(
        latmin), str_6d(lngmin), str_6d(latmax))
    return bound


def bound2coords(bound):
    crds_str = [coords.split(',') for coords in bound.split('|')]
    crds_float = [[float(c[0]), float(c[1])] for c in crds_str]
    return crds_float


def div_by_half(bound):
    ori_crds = bound2coords(bound)
    lngmax, latmin = ori_crds[0]
    lngmin, latmax = ori_crds[1]
    latres = abs(latmax - latmin) / 2
    lngres = abs(lngmax - lngmin) / 2

    bounds = []
    for dlt_lng in [0, lngres]:
        for dlt_lat in [0, latres]:
            lt_lng = lngmax - dlt_lng
            lt_lat = latmin + dlt_lat
            bounds.append(coords2bound(lt_lng, lt_lat,
                          lt_lng - lngres, lt_lat + latres))
    return bounds


def mesh_points(boundary, resolution=0.015, resume_from=None, set_bound=None):
    # determine maximum edges
    bounds = list(boundary.total_bounds)

    # update lat and lng
    if set_bound:
        ori_crds = bound2coords(set_bound)
        bounds[2], bounds[1] = ori_crds[0]
        bounds[0], bounds[3] = ori_crds[1]

    boundary = boundary.buffer(resolution * 1.1)
    # construct a rectangular mesh
    for lat in np.arange(bounds[1], bounds[3] - resolution, resolution):
        if resume_from and lat < resume_from[1] - resolution:
            continue
        for lng in np.arange(bounds[0] + resolution, bounds[2], resolution):
            if resume_from and lat <= resume_from[1] and lng < resume_from[0]:
                continue
            point = Point((round(lng, 6), round(lat, 6)))
            try:
                if boundary.contains(point):
                    yield point
            except:
                try:
                    if boundary.contains(point).any():
                        yield point
                except Exception as e:
                    print('contains() err', e)


class AmapPoi(object):
    def __init__(self, adcode, resolution=0.015, start=17, end=9,
                 city_boundary=None,
                 type_code_strs=None,
                 typecodes=None,
                 super_typecodes=None):
        self.type_code_strs = type_code_strs
        self.typecodes = typecodes
        self.super_typecodes = super_typecodes
        self.key = amap_key
        self.year = str(date.today().year)
        self.adcode = str(adcode)
        self.resolution = resolution  # Smallest search grid (by degree)
        self.wake_time = start
        self.sleep_time = end
        self.random_sleep_time = 0.05
        self.rds_key = 'progress_{}:{}:'.format(self.year, 'poi_amap')
        self.city_boundary = city_boundary if city_boundary is not None else \
            get_gdf(cls='boundary_city', adcode=adcode, year=2022)

    def is_done(self):
        # try:
        #     codes = self.coll.distinct('typecode')
        #     supercodes = set([c[:2] for c in codes])
        #     return len(supercodes) >= 20
        # except:
        #     print('Failed to check completeness')
        #     return False
        return False

    def test_none_type(self, pid):
        doc = self.coll.find_one({"PID": pid})
        return doc is None

    def random_sleep(self):
        if random.random() < self.random_sleep_time:
            time.sleep(random.random() * 100)

    # @add_alert(subject="Amap poi error")
    def poi_by_grid(self, adcode, bound,
                    super_typecodes: list = None,
                    typecodes: list = None,
                    type_code_strs: list = None):
        """
        super_typecodes: 大类int，eg. [1,7,10]
        typecodes: 六位string, eg. ['110000', '070000', '060400', '060700']
        type_code_strs: eg. '110000|070000|060400|060700|060200|080400|080402|080500'
        """
        if not type_code_strs:
            if typecodes:
                type_code_strs = ['|'.join(typecodes)]  # 所有小类一起爬
            else:
                if not super_typecodes:
                    # TODO combine minor types
                    super_typecodes = list(range(1, 21))
                type_code_strs = [str(t).zfill(
                    2) + '0000' for t in super_typecodes]  # 大类分别爬

        failed_bounds = []
        if type(bound) is list:
            bound = bound.pop(0)

        print("Querying bound ", bound)

        for type_code_str in type_code_strs:
            for pages in range(100):
                # print('Querying Page ', str(pages))
                url = 'http://restapi.amap.com/v3/place/polygon?types=' + str(
                    type_code_str) + '&polygon=' + bound + '&extensions=all&offset=25&page=' + str(
                    pages + 1) + '&output=json&key=' + self.key

                try:
                    self.random_sleep()  # To slow down
                    r = requests.get(url, proxies=get_proxy())
                    data = r.json()
                    while data['status'] == '0':
                        print(data['info'])
                        time.sleep(20000)
                        data = requests.get(url).json()
                except Exception as e:
                    print(bound, ' failed! error: ', e)
                    # traceback.print_exc()
                    failed_bounds.append(bound)
                    break
                try:
                    if data['pois']:  # Check if the list is empty
                        # search smaller grid if this grid is too large
                        if int(data['count']) >= 800:
                            print(bound, ' is too large')
                            for sub_b in div_by_half(bound):
                                b = self.poi_by_grid(
                                    adcode, sub_b, type_code_strs=[type_code_str])
                                if b:
                                    failed_bounds.append(b)
                            break
                        try:
                            for line in data['pois']:
                                poi = {'PID': 'null', 'name': 'null', 'type': 'null',
                                       'typecode': 'null',
                                       'address': 'null', 'lng': 0, 'lat': 0}
                                # no data in database, go on
                                if self.test_none_type(line["id"]) is True:
                                    poi["adcode"] = adcode
                                    poi["PID"] = line["id"]
                                    poi["name"] = comma_replace(line["name"])
                                    poi["type"] = line["type"]
                                    poi["typecode"] = line["typecode"]
                                    poi["address"] = comma_replace(
                                        line["address"])
                                    lat_gcj = str(
                                        line["location"]).split(",")[1]
                                    lng_gcj = str(
                                        line["location"]).split(",")[0]
                                    poi["lng"], poi["lat"] = gcj02towgs84(
                                        float(lng_gcj), float(lat_gcj))
                                    poi['coll_year'] = YEAR
                                    poi['source'] = 'amap'
                                    poi['class'] = 'poi'
                                    if 'parent' in line.keys() and type(line['parent']) is str:
                                        poi['parent'] = line['parent']
                                    if 'childtype' in line.keys() and type(line['childtype']) is str:
                                        poi['childtype'] = line['childtype']

                                    partition = random.randint(0, 3)
                                    future = PRODUCER.send(
                                        TOPIC, partition=partition, value=poi)
                                    result = future.get(timeout=10)
                                    print(poi)
                                    # self.db[coll_name].insert_one(poi)
                                else:  # data exists, next line
                                    print(
                                        "Data exists, processing to the next line...")
                                    continue
                        except TypeError:
                            pass
                    else:
                        # print('Empty page! ')
                        break
                except KeyError:
                    print(
                        'key error in data[\'pois\']... breaking the loop...')
                    break
        return failed_bounds

    def crawl_by_subtree(self, adcode, bound, resolution=0.015):
        ori_crds = bound2coords(bound)
        lngmax, latmin = ori_crds[0]
        lngmin, latmax = ori_crds[1]

        failed_bounds = []
        doc = self.coll.find_one(
            {'lat': {'$gt': latmin, '$lt': latmax}, 'lng': {'$gt': lngmin, '$lt': lngmax}})
        if latmax - latmin > resolution or lngmax - lngmin > resolution:
            #  get smaller bounds if this bound is too large and has poi
            if doc:
                for sub_b in div_by_half(bound):
                    b = self.crawl_by_subtree(
                        adcode, sub_b, resolution=resolution)
                    if b:
                        failed_bounds.append(b)
            #  get mesh points and crawl by grid if this bound is too large and has not poi
            else:
                for point in mesh_points(self.city_boundary, resolution=resolution, set_bound=bound):
                    lngmax, latmin = list(point.coords)[0]
                    lngmin = lngmax - resolution
                    latmax = latmin + resolution
                    sub_bound = '{},{}|{},{}'.format(str_6d(lngmax), str_6d(
                        latmin), str_6d(lngmin), str_6d(latmax))
                    b = self.poi_by_grid(adcode, sub_bound)
                    if b:
                        failed_bounds.append(b)
        else:
            # pass if this bound is small and has poi
            if doc:
                print(bound, "Data exists, processing to the next grid")
                return

            # crawl by grid directly if this bound is small and has not poi
            point = Point((round(lngmax, 6), round(latmin, 6)))
            try:
                if self.city_boundary.contains(point):
                    failed_bounds.extend(self.poi_by_grid(adcode, bound))
            except:
                try:
                    if self.city_boundary.contains(point).any():
                        failed_bounds.extend(self.poi_by_grid(adcode, bound))
                except Exception as e:
                    print('contains() err', e)
            return failed_bounds

    def find_last_coord(self):
        lngmax = 0
        latmax = 0
        try:
            last_poi = self.coll.find_one({}, sort=[('_id', -1)])
            lngmax = max(last_poi['lng'], lngmax)
            latmax = max(last_poi['lat'], latmax)
        except:
            pass
        return [lngmax, latmax]

    # @add_alert(subject="Amap poi error")
    def poi_by_city(self, subtree=False):

        # Sleep until wake time
        hour = datetime.now().hour
        while self.sleep_time <= hour < self.wake_time:
            time.sleep(1800)
            hour = datetime.now().hour

        adcode = str(self.adcode)
        # log start
        subkey = self.rds_key + adcode
        prog = rds.hgetall(subkey)
        if not prog:
            prog = {'progress': 0, 'converted': 'False'}
            rds.hmset(subkey, prog)
        # elif int(prog[b'progress'].decode('utf-8')) == 100:
        #     print(self.adcode, 'done')
        #     return

        work_queue = []
        if not subtree:
            # start from last crawled
            # last_coord = self.find_last_coord()
            last_coord = None  # temp
            # crawl by fishnet
            for point in mesh_points(self.city_boundary, self.resolution, resume_from=last_coord):
                lngmax, latmin = list(point.coords)[0]
                lngmin = lngmax - self.resolution
                latmax = latmin + self.resolution
                bound = '{},{}|{},{}'.format(str_6d(lngmax), str_6d(
                    latmin), str_6d(lngmin), str_6d(latmax))
                failed = self.poi_by_grid(adcode, bound,
                                          super_typecodes=self.super_typecodes,
                                          typecodes=self.typecodes,
                                          type_code_strs=self.type_code_strs)
                if failed:
                    work_queue.extend(failed)
        else:
            # crawl by subtree
            city_bounds = list(self.city_boundary.bounds)
            city_bound = '{},{}|{},{}'.format(str_6d(city_bounds[2]), str_6d(city_bounds[1]), str_6d(city_bounds[0]),
                                              str_6d(city_bounds[3]))
            failed = self.crawl_by_subtree(
                adcode, city_bound, resolution=self.resolution)
            if failed:
                work_queue.extend(failed)

        # deal with failed grid
        tried = 0
        while len(work_queue) > 0 and tried < 100:
            b = self.poi_by_grid(adcode, work_queue.pop(0),
                                 super_typecodes=self.super_typecodes,
                                 typecodes=self.typecodes,
                                 type_code_strs=self.type_code_strs)
            if b:
                work_queue.extend(b)
                tried += 1
            else:
                tried = 0

        # Log finish
        # if self.is_done(adcode):
        prog = rds.hgetall(subkey)
        if prog[b'progress'] != b'100':
            prog = {'progress': 100, 'converted': 'False'}
            rds.hmset(subkey, prog)

        print(work_queue)
        return work_queue


if __name__ == '__main__':
    AmapPoi(510100, 0.01, start=0, end=24).poi_by_city(subtree=True)
