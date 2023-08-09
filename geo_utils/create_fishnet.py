# -*- coding: utf-8 -*-
'''
Created on  11:04:50, 07/08 2023

@Author  :   kingsley
@Email :   kingsleyl0107@gmail.com
'''

import geopandas as gpd
from shapely import geometry


def create_fishnet(gdf, grid_size=100):
    """_summary_

    Args:
        gdf (_type_): _research boundary_
        grid_size (int, optional): _grid size_. Defaults to 100(meters).

    Returns:
        _type_: _caution: the crs of fishnet retains origin gdf's crs_
    """
    crs = gdf.crs
    # Get minX, minY, maxX, maxY
    total_bounds = gdf.total_bounds
    minX, minY, maxX, maxY = total_bounds

    # Create a fishnet
    x, y = (minX, minY)
    geom_array = []

    while y <= maxY:
        while x <= maxX:
            geom = geometry.Polygon(
                [(x, y), (x, y + grid_size), (x + grid_size, y + grid_size), (x + grid_size, y), (x, y)])
            geom_array.append(geom)
            x += grid_size
        x = minX
        y += grid_size

    fishnet = gpd.GeoDataFrame(geom_array, columns=['geometry']).set_crs(crs)
    return fishnet