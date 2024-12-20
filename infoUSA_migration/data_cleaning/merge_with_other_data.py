# combine migration identification file with other charcteristics to generate full sample

import pandas as pd
import numpy as np
import os
import string
import time as time
from datetime import datetime

f = open("panel combine log.txt","w+")
print("date and time =", datetime.now().strftime("%d/%m/%Y %H:%M:%S"),file=f)

pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows', 100)

# coastal damage
df_county_level=pd.read_csv(r'D:\combined data\09102024 data\panel_county_level_control_for_migration.csv')

# metropolitan data based on zipcode
df_zip=pd.read_csv(r'D:\combined data\09102024 data\zip_metro.csv')

# new area assignation
df_area=pd.read_csv('D:/combined data/county_geo_update.csv')

# sample low-income households to decrease total size
df1 = pd.DataFrame()
count = 0
all=0
top_10=0
bottom_90=0

for chunk in pd.read_csv(r'D:\Pyproject\infoUSA\data cleaning\panel data\2015-2021_annual_migration_panel_identification_subsample.csv', sep=',', index_col=0,
                         chunksize=1000000, encoding='utf-8'):
    # REPLACING BLANK SPACES AT COLUMNS' NAMES FOR SQL OPTIMIZATION
    # print(chunk)
    chunk = chunk.rename(columns={c: c.replace(' ', '') for c in chunk.columns})

    # # sample by income and wealth
    # all+= len(chunk)
    # chunk1 = chunk[((chunk['FIND_DIV_1000'] > 176) | (chunk['WEALTH_FINDER_SCORE'] > 3200)) ].copy()
    # chunk1['weight']=1
    # top_10+=len(chunk1)
    # chunk2 = chunk[~((chunk['FIND_DIV_1000'] > 176) | (chunk['WEALTH_FINDER_SCORE'] > 3200))].sample(frac=0.40, random_state=1).copy()
    # chunk2['weight'] = 2.5
    # bottom_90+=len(chunk2)
    # chunk = chunk2.append(chunk1)

    # ND
    chunk = pd.merge(chunk, df_county_level, how='left', left_on=['STATE_x', 'GE_ALS_COUNTY_CODE_2010_x','year_x'],
                     right_on=['state', 'county','year'])
    chunk.drop(['state', 'county'], axis=1, inplace=True)


    # metropolitan area
    chunk = chunk.merge(df_zip, left_on='ZIP_x', right_on='ZCTA5')
    chunk = chunk.merge(df_zip, left_on='ZIP_y', right_on='ZCTA5')

    # # wind field
    # chunk = pd.merge(chunk, df_wind, how='left', left_on=['STATE_x', 'GE_ALS_COUNTY_CODE_2010_x','year_x'],
    #                  right_on=['state', 'county','year'])
    # chunk.drop(['state', 'county'], axis=1, inplace=True)

    # # only contains east coast
    # chunk.drop(chunk[(chunk['area_x'] >3) |(chunk['area_x']==2)].index, inplace=True)
    chunk = chunk.apply(pd.to_numeric,errors='ignore', downcast='signed')
    chunk = chunk.apply(pd.to_numeric,errors='ignore', downcast='float')
    # print(chunk.info(memory_usage='deep'))
    count += 1

    df1 = df1.append(chunk)
    # df1 = df1.apply(pd.to_numeric, downcast='signed')
    # df1 = df1.apply(pd.to_numeric, downcast='float')
    print(df1.info(memory_usage='deep'),file=f)
    print(len(df1))
#
print(all,file=f)
print(top_10,file=f)
print(bottom_90,file=f)
df1.to_csv('natural_disaster_and_migration_panel_20_sample_v2_2015.csv', encoding='utf-8',index=False)

