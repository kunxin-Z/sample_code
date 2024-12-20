# generate village level mangrove distribution based on zonal statistics

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

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

gdf_village = gpd.read_file(
    r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output\village_2011_coast.shp')
gdf_village.reset_index(names='IN_FID', inplace=True)
gdf_village['IN_FID']=gdf_village['IN_FID']+1


# ******************************************************************************************************************** #
# *********************************  distance from village to coastline  ********************************************* #
# ******************************************************************************************************************** #
inputdir_tmf=r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output'
filenames=os.listdir(inputdir_tmf)

for buffer in ['1600','3200']:
    df_output = pd.DataFrame()
    for filename in filenames:
        if filename[-4:]=='.csv' and 'new_village_shore_buffer' in filename and 'rade' not in filename and 'rest' not in filename and buffer in filename:
            print(filename)
            year=filename.split('_')[5][:4]
            print(year)
            df_deforest=pd.read_csv(inputdir_tmf+'/'+filename)
            cols=df_deforest.columns

            # add columns if needed
            if 'code_6' not in cols:
                print('code_6')
                df_deforest['code_6']=0

            # fillna and switch to percentage
            df_deforest.fillna(0,inplace=True)
            df_deforest.set_index('index',inplace=True)

            df_deforest['total'] = df_deforest.sum(axis=1)

            # classify regrowth and undistrubed mangrove and forest and mangrove and forest
            df_deforest['mann']=df_deforest['code_6']+df_deforest['code_18']
            df_deforest['fann'] = df_deforest['code_5'] + df_deforest['code_17']

            # classify degrade
            df_deforest['gmann'] = df_deforest['code_10']
            df_deforest['gfann'] = df_deforest['code_9']

            # classify deforest
            df_deforest['dmann'] = df_deforest['code_14']
            df_deforest['dfann'] = df_deforest['code_13']

            df_deforest['year']=year

            df_deforest=df_deforest[['year','mann','fann','gmann','gfann','dmann','dfann']].copy()
            df_output=pd.concat([df_output,df_deforest])

    df_output.to_csv('village_shore_'+buffer+'_annual_deforest.csv')

# ******************************************************************************************************************** #
# ***********************  shoretest distance from village to coastline  ********************************************* #
# ******************************************************************************************************************** #
inputdir_tmf=r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output_polygon_distance'
filenames=os.listdir(inputdir_tmf)

for buffer in ['1600','3200']:
    df_output = pd.DataFrame()
    for filename in filenames:
        if filename[-4:]=='.csv' and '1950' not in filename and 'new_village_shore' in filename and 'rade' not in filename and 'rest' not in filename and buffer in filename:
            print(filename)
            year=filename.split('_')[5][:4]
            print(year)
            df_deforest=pd.read_csv(inputdir_tmf+'/'+filename)
            cols=df_deforest.columns

            # merge with distance data to generate index
            df_deforest = df_deforest.merge(gdf_village[['IN_FID', 'index']], on='IN_FID', how='left')
            df_deforest.drop('IN_FID',axis=1,inplace=True)


            # add columns if needed
            if 'code_6' not in cols:
                print('code_6')
                df_deforest['code_6']=0

            # fillna and switch to percentage
            df_deforest.fillna(0,inplace=True)
            df_deforest.set_index('index',inplace=True)

            df_deforest['total'] = df_deforest.sum(axis=1)

            # classify regrowth and undistrubed mangrove and forest and mangrove and forest
            df_deforest['mann']=df_deforest['code_6']+df_deforest['code_18']
            df_deforest['fann'] = df_deforest['code_5'] + df_deforest['code_17']

            # classify degrade
            df_deforest['gmann'] = df_deforest['code_10']
            df_deforest['gfann'] = df_deforest['code_9']

            # classify deforest
            df_deforest['dmann'] = df_deforest['code_14']
            df_deforest['dfann'] = df_deforest['code_13']

            df_deforest['year']=year

            df_deforest=df_deforest[['year','mann','fann','gmann','gfann','dmann','dfann']].copy()
            df_output=pd.concat([df_output,df_deforest])

    df_output.to_csv('village_shore_polygon_'+buffer+'_annual_deforest.csv')


# ******************************************************************************************************************** #
# ************************************  percentage within village  *************************************************** #
# ******************************************************************************************************************** #
inputdir_tmf=r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output'
filenames=os.listdir(inputdir_tmf)

df_output = pd.DataFrame()
for filename in filenames:
    if filename[-4:]=='.csv' and 'village_mangrove' in filename and 'rade' not in filename and 'rest' not in filename:
        print(filename)
        year=filename.split('_')[2][:4]
        print(year)
        df_deforest=pd.read_csv(inputdir_tmf+'/'+filename)
        cols=df_deforest.columns

        # add columns if needed
        if 'code_6' not in cols:
            print('code_6')
            df_deforest['code_6']=0

        # fillna and switch to percentage
        df_deforest.fillna(0,inplace=True)
        df_deforest.set_index('index',inplace=True)

        df_deforest=df_deforest.div(df_deforest.sum(axis=1), axis=0)

        # classify regrowth and undistrubed mangrove and forest and mangrove and forest
        df_deforest['mann']=df_deforest['code_6']+df_deforest['code_18']
        df_deforest['fann'] = df_deforest['code_5'] + df_deforest['code_17']

        # classify degrade
        df_deforest['gmann'] = df_deforest['code_10']
        df_deforest['gfann'] = df_deforest['code_9']

        # classify deforest
        df_deforest['dmann'] = df_deforest['code_14']
        df_deforest['dfann'] = df_deforest['code_13']

        df_deforest['year']=year

        df_deforest=df_deforest[['year','mann','fann','gmann','gfann','dmann','dfann']].copy()
        df_output=pd.concat([df_output,df_deforest])

df_output.to_csv('village_annual_deforest.csv')


# ******************************************************************************************************************** #
# ************************************  IV  *************************************************** #
# ******************************************************************************************************************** #
inputdir_tmf=r'C:\Users\zhu.2906\Documents\ArcGIS\Projects\shrug_india\output'
filenames=os.listdir(inputdir_tmf)

df_output = pd.DataFrame()
for filename in filenames:
    if filename[-4:]=='.csv' and 'iv_1600_' in filename and 'rade' not in filename and 'rest' not in filename:
        print(filename)
        year=filename.split('_')[2][:4]
        print(year)
        df_deforest=pd.read_csv(inputdir_tmf+'/'+filename)
        cols=df_deforest.columns

        # add columns if needed
        if 'code_6' not in cols:
            print('code_6')
            df_deforest['code_6']=0

        # fillna and switch to percentage
        df_deforest.fillna(0,inplace=True)
        df_deforest.set_index('index',inplace=True)

        df_deforest=df_deforest.div(df_deforest.sum(axis=1), axis=0)

        # classify regrowth and undistrubed mangrove and forest and mangrove and forest
        df_deforest['mann']=df_deforest['code_6']+df_deforest['code_18']
        df_deforest['fann'] = df_deforest['code_5'] + df_deforest['code_17']

        # classify degrade
        df_deforest['gmann'] = df_deforest['code_10']
        df_deforest['gfann'] = df_deforest['code_9']

        # classify deforest
        df_deforest['dmann'] = df_deforest['code_14']
        df_deforest['dfann'] = df_deforest['code_13']

        df_deforest['year']=year

        df_deforest=df_deforest[['year','mann','fann','gmann','gfann','dmann','dfann']].copy()
        df_output=pd.concat([df_output,df_deforest])

df_output.to_csv('village_iv_deforest.csv')