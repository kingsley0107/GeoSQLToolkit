import arcpy


######################################基础配置区,若不修改选中的osm_fclass / qq_subtype ，修改此处路径即可。#################################
# 指定gdb文件夹路径

# 建议输入完整路径，相对路径似乎有点问题,此处屏蔽本地计算机文件路径，使用相对路径
FILE_ROOT = r"C:\Users\20191\Desktop\github\road_regularization\data\测试过程数据库/"
# 指定新建gdb名称
DATABASE_NAME = "ROAD_OPTIMIZE2.gdb"
# 指定目标城市基础数据路径,文件夹内数据命名格式如下
# 边界数据: xiangcheng.shp
ROAD_DATA = r"C:\Users\20191\Desktop\github\road_regularization/data/测试路网数据/"
BOUNDARY_DATA = r"C:\Users\20191\Desktop\github\road_regularization/data/测试边界数据/"
OUTPUT_PATH = r"C:\Users\20191\Desktop\github\road_regularization/data/测试输出数据/"
######################################配置区结束#################################

# 最最最主要的道路类别

# 表示道路类型的字段
ROAD_TYPE_FIELD = "dj"

# TPYES FOR MIXED MODE
OSM_MAIN_FCLASS = [
    "1",
    "2",
    "3",
    "4",
    "5",
]

# # TYPES FOR DIVIDED MODE
# OSM_MAIN_FCLASS_NO_HIGH = ['Unknown', 'Unclassified', 'Classified Unnumbered','Not Classified']
# OSM_MAIN_FCLASS_HIGH = ['A Road', 'B Road']

# 最终数据中需要保留的字段
fields_to_keep = ["OBJECTID", "dm", "SHAPE", "SHAPE_Length"]
#
# MERGING_MAP = {
#     'A Road': 1,
#     'B Road': 2,
#     'Classified Unnumbered': 3,
#     'Unknown': 4,
#     'Not Classified': 5
# }


# config proj epsg code
PROJ_CRS = 3857
GEO_CRS = 4326
# config spatial ref
Project_ref = arcpy.SpatialReference(PROJ_CRS)
Geographic_ref = arcpy.SpatialReference(GEO_CRS)
