import requests
from tqdm import tqdm  # 显示进度条
from transcoords import bd092wgs84


def geocoding(addr, city, key_num=0):
    geo_key = ['BVtxhABS7uv1WHGyU0xqU8SqT05oFMQi']
    geo_url = f'https://api.map.baidu.com/geocoding/v3/?address={addr}&city={city}&output=json&ak={geo_key[key_num]}'
    res = requests.get(geo_url).json()
    if res['status'] == 0:
        lng = res['result']['location']['lng']
        lat = res['result']['location']['lat']
        wgs84_xy = bd092wgs84(lng, lat)
        lng = wgs84_xy[0]
        lat = wgs84_xy[1]
        print(lng,lat)
    elif res['status'] == 4 and key_num == 0:
        print('配额校验失败')
        return geocoding(addr, city, 1)  # try second key
    else:
        print('逆地址解析失败, status:', res['status'])
        return 0, 0
    return lng, lat


def df_geocoding(df, addr_col, city):
    if 'Longitude' in df.columns and 'Latitude' in df.columns:
        return df
    print("Geocoding...")
    unique_addr = list(set(df[addr_col].tolist()))
    addr_geo = {addr: geocoding(addr, city) for addr in tqdm(unique_addr)}
    df['geo'] = df[addr_col].apply(lambda x: addr_geo[x])
    df['long_wgs'] = df['geo'].apply(lambda x: x[0])
    df['lat_wgs'] = df['geo'].apply(lambda x: x[1])
    df = df.drop([addr_col, 'geo'], axis=1)

    return df


geocoding("北京大学", "北京市")
