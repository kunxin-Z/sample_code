# generate wind field data at centroid of each village in India
# currenly, we majorly use functions from Hsiang & Jina (2014) and Pelli et al (2023)
# v_1 generate cyclone impact from <=3, >=4 and total
# v_2 generate monthly data

# ******************************************************************************************************************** #
# ****************************************  Setting  ***************************************************************** #
import pandas as pd
import numpy as np
import os
import string
import time as time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import LineString
from itertools import product

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 700)


# ***********************************  read and clean data  ********************************************************** #
# read cycloned data around India
bbox = (
    65,0,100,40
)
gdf_cyclone=gpd.read_file(r'C:\Users\zhu.2906\OneDrive - The Ohio State University\pythonProject\India_mangroves_python\data\cyclone\IBTrACS.ALL.list.v04r00.lines.shp'
                          ,bbox=bbox)
print(gdf_cyclone.dtypes)
print(gdf_cyclone.head(10))
print(len(gdf_cyclone))

# change to EPSG:24378
gdf_cyclone=gdf_cyclone.to_crs(epsg=7755)


# Generate maximum wind speed data for each event
df_cyclone_all=pd.DataFrame(gdf_cyclone.groupby('SID')['USA_SSHS'].max())
df_cyclone_all.columns=['USA_SSHS_max']

# merge to gdf_cyclone
gdf_cyclone=gdf_cyclone.merge(df_cyclone_all,on=['SID'],how='left')

# clean data
# drop events before 2000
gdf_cyclone.drop(gdf_cyclone[gdf_cyclone['year'] <2000].index,inplace=True)

# drop events with lower than -1 level
gdf_cyclone.drop(gdf_cyclone[gdf_cyclone['USA_SSHS_max'] <-1].index,inplace=True)

# get temporal resolution (all data are recorded at 3 hour temporal resolution)
gdf_cyclone['aggregate_hour']=gdf_cyclone['hour']+gdf_cyclone['day']*24
gdf_cyclone['diff'] = gdf_cyclone.groupby('SID')['aggregate_hour'].diff()

print(gdf_cyclone.groupby(['diff'])['SID'].count())
gdf_cyclone.drop(['aggregate_hour','diff'],axis=1,inplace=True)
print(len(gdf_cyclone))


# ***********************************  divide line features by 6 points  ********************************************* #
gdf_cyclone_p = gpd.GeoDataFrame()
for n in np.arange(0, len(gdf_cyclone)):

    # for each line, get point at 1/12, ... 11/12 distance
    line_geom = LineString(gdf_cyclone.geometry.iloc[n].coords)
    distances = list(np.arange(line_geom.length / 12, line_geom.length, line_geom.length / 6))

    # generate points data with wind speed information
    points = [line_geom.interpolate(d) for d in distances]
    point_data = gpd.GeoDataFrame(geometry=points, crs=gdf_cyclone.crs)

    # for each point, copy needed line data to it
    for col in ['SID', 'NAME', 'USA_WIND', 'USA_PRES', 'USA_SSHS', 'USA_SSHS_max', 'SEASON', 'month', 'day', 'hour']:
        column_index = gdf_cyclone.columns.get_loc(col)
        point_data[col] = gdf_cyclone.iloc[n, column_index]

    gdf_cyclone_p = pd.concat([gdf_cyclone_p, point_data], ignore_index=True)

# get X, Y data
gdf_cyclone_p['X_point'] = gdf_cyclone_p.geometry.x
gdf_cyclone_p['Y_point'] = gdf_cyclone_p.geometry.y

# ***********************************generate wind field data based on centroid*************************************** #
gdf_village=gpd.read_file(r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output\village_2011_coast.shp')

# get only the centroid of each village
gdf_village=gdf_village.to_crs(epsg=7755)
gdf_village['X_centroid']=gdf_village.geometry.centroid.x
gdf_village['Y_centroid']=gdf_village.geometry.centroid.y

# merge with all points
df_village=pd.DataFrame(gdf_village[['index','X_centroid','Y_centroid']].copy())
df_village['1']=1

##### natural science function
# wind field function
def wind_speed(row):
    if row['distance'] <= 26.9978:
        return row['USA_WIND'] * row['distance'] / 26.9978
    if row['distance'] > 26.9978:
        return row['USA_WIND'] * (row['distance'] / 26.9978) ** -0.5


# Pelli_index function (to transfer value from half an hour to an hour, we divide wind field index by 2)
def cyclone_index(row, threshold, power):
    if row['wind_speed'] > threshold:
        return (row['wind_speed'] - threshold) ** power/2
    else:
        return 0


# get wind field data
gdf_cyclone_p['1'] = 1

dfs = np.array_split(df_village, 400)

# ***********************************  get wind field data from two classes of cyclone  ****************************** #
df_output = pd.DataFrame()
n=0
for df in dfs:
    n+=1
    print(n)
    df = df.merge(gdf_cyclone_p[
                      ['SID', 'SEASON', 'month', 'hour', 'USA_WIND', 'USA_SSHS', 'USA_SSHS_max', 'X_point', 'Y_point',
                       '1']], on=['1'], how='outer')
    df.drop('1', axis=1, inplace=True)

    # generate distance in miles
    df['distance'] = ((df['X_centroid'] - df['X_point']) ** 2 + (
                df['Y_centroid'] - df['Y_point']) ** 2) ** 0.5 / 1609.34

    # generate local wind speed based on Pelli et al. (2023)
    df['wind_speed'] = df.apply(wind_speed, axis=1)
    print(df[(df['SEASON']>=2007)&(df['SEASON']<=2020)]['wind_speed'].max())
    df['wind_speed_33']= df['wind_speed'].apply(lambda x: 1 if x >= 33 else 0)
    df['wind_speed_50'] = df['wind_speed'].apply(lambda x: 1 if x >= 50 else 0)
    df['wind_speed_64'] = df['wind_speed'].apply(lambda x: 1 if x >= 64 else 0)
    df['wind_speed_100'] = df['wind_speed'].apply(lambda x: 1 if x >= 100 else 0)
    df['wind_speed_130'] = df['wind_speed'].apply(lambda x: 1 if x >= 130 else 0)


    # calculate exposure based on Pelli et al,
    df['wf_33_2'] = df.apply(cyclone_index, args=(33, 2,), axis=1)
    df['wf_33_3'] = df.apply(cyclone_index, args=(33, 3,), axis=1)

    df['wf_50_2'] = df.apply(cyclone_index, args=(50, 2,), axis=1)
    df['wf_50_3'] = df.apply(cyclone_index, args=(50, 3,), axis=1)

    df['wf_64_2'] = df.apply(cyclone_index, args=(64, 2,), axis=1)
    df['wf_64_3'] = df.apply(cyclone_index, args=(64, 3,), axis=1)

    # calculate exposure based on Hsiang cubic term
    df['wf_0_2'] = df.apply(cyclone_index, args=(0, 2,), axis=1)
    df['wf_0_3'] = df.apply(cyclone_index, args=(0, 3,), axis=1)



    df = pd.DataFrame(df.groupby(['index', 'SEASON','month']).sum())

    df_output = pd.concat([df_output, df])

df_output[['wind_speed_33','wf_33_2','wf_33_3','wind_speed_50','wf_50_2','wf_50_3','wind_speed_64','wf_64_2','wf_64_3',
           'wf_0_2','wf_0_3','wind_speed_100','wind_speed_130']].to_csv('cyclone_index.csv')
