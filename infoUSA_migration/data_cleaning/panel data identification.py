# generate panel data from 2015-2020
import pandas as pd
import numpy as np
import os
import string
import time as time
from datetime import datetime

f = open("Panel data construction log.txt","w+")
print("date and time =", datetime.now().strftime("%d/%m/%Y %H:%M:%S"),file=f)
pd.set_option('display.max_columns', None)

# get prefix of input_dir
inputdir_prefix = 'D:/Pyproject/infoUSA/generation data/'

# get county assignation for coastal regions
df_area=pd.read_csv('D:/combined data/county_geo_update.csv')

# function to return all household level data from any given year given inputdir and command
def output_total_df(inputdir_prefix, year, command='Default'):
    inputdir = inputdir_prefix + year

    filenames = os.listdir(inputdir)

    df_empty = pd.DataFrame()
    print(year,file=f)
    all=0
    no_vacant=0

    for file in filenames:
        if 'csv' in file:
            print(file)
            # print(file)
            # start = time.time()
            df = pd.read_csv(inputdir + '/' + file)
            # print(df.dtypes)

            if len(df)>1:
                # drop vacant household
                all += len(df)
                df.drop(df[df['VACANT'] == 1].index, inplace = True)
                df.drop(['VACANT'], axis=1, inplace=True)
                no_vacant += len(df)

                if command == 'coast':
                    # drop non coastal county
                    df = df[df['area_new'].isin([1, 2, 3, 5])]

                if command == 'east_coast':
                    # drop non coastal county
                    df = df[df['area_new'].isin([1,  3])]

                if command == 'ID_check':
                    # only need familyID
                    df = df[['FAMILYID']]

                # modify data to save space
                # print(df.info(memory_usage='deep'))
                df = df.apply(pd.to_numeric,errors='ignore' ,downcast='signed')
                # print(df.info(memory_usage='deep'))

                if len(df) > 1:
                    df_empty = df_empty.append(df)

                # print(df_empty.info(memory_usage='deep'))
                # end = time.time()
                # print(start - end)

    # print(df_empty.info(memory_usage='deep'))
    # calculate vacany rate for each year
    print(all,file=f)
    print(no_vacant, file=f)
    return df_empty

# function to return annual migration sample based on two consecutive year of data
def migration_sample(year_pre,year_post,sample=1,state=0):
    print('migration sample from'+str(year_pre)+'to'+str(year_post))

    start = time.time()

    # given the study area (only get data for households living in east coast)
    df_pre = output_total_df(inputdir_prefix, str(year_pre),command='east_coast')
    print(str(year_pre), file=f)
    print(len(df_pre), file=f)
    end = time.time()
    print(df_pre.info(memory_usage='deep'))
    print(end - start)
    print('1')

    start = time.time()
    df_post = output_total_df(inputdir_prefix, str(year_post))
    print(df_post.info(memory_usage='deep'))
    print(str(year_post))
    print(len(df_post))
    end = time.time()
    print(end - start)
    print('2')

    # drop data if state_list does not contain variable
    if state!=0:
        df_pre.drop(df_pre[~(df_pre['STATE'].isin(state))].index,inplace=True)

    df_pre=df_pre[['FAMILYID', 'HEAD_HH_AGE_CODE', 'CHILDREN_IND',
               'FIND_DIV_1000','OWNER_RENTER_STATUS','ESTMTD_HOME_VAL_DIV_1000',
               'STATE', 'GE_ALS_COUNTY_CODE_2010', 'GE_CENSUS_LEVEL_2010','ZIP',
               'Ethnicity_Code_1', 'CITY','year','area_new','shoreline']]\
    .merge(df_post[['FAMILYID','STATE','CHILDREN_IND', 'GE_ALS_COUNTY_CODE_2010', 'ZIP',
             'CITY','year','area_new','shoreline']],how='inner',on=['FAMILYID'])

    # generate quantile range for suitable sample
    df_pre_quantile=df_pre.drop(df_pre[df_pre['OWNER_RENTER_STATUS'] == 5].index)
    df_pre_quantile=df_pre_quantile.drop(df_pre_quantile[((df_pre_quantile['HEAD_HH_AGE_CODE'] <= 25) | (df_pre_quantile['HEAD_HH_AGE_CODE'] >= 60))].index)
    income_quantiles=[0, np.nanquantile(df_pre_quantile[['FIND_DIV_1000']], 0.5), np.nanquantile(df_pre_quantile[['FIND_DIV_1000']], 0.9),
     np.nanquantile(df_pre_quantile[['FIND_DIV_1000']], 0.99), 500]
    # wealth_quantiles = [0, np.nanquantile(df_pre_quantile[['WEALTH_FINDER_SCORE']], 0.5),
    #                     np.nanquantile(df_pre_quantile[['WEALTH_FINDER_SCORE']], 0.9),
    #                     np.nanquantile(df_pre_quantile[['WEALTH_FINDER_SCORE']], 0.99), 500]
    del df_pre_quantile
    print(income_quantiles,file=f)
    # print(wealth_quantiles, file=f)

    # sample data if needed
    if sample!=1:
        df_pre=df_pre.sample(frac=sample,random_state=1).copy()

        
    return df_pre

df_output=migration_sample(2015,2016,sample,state_list)
df2012=migration_sample(2016,2017,sample,state_list)
df_output=df_output.append(df2012)
del df2012
df2013=migration_sample(2017,2018,sample,state_list)
df_output=df_output.append(df2013)
del df2013
df2014=migration_sample(2019,2020,sample,state_list)
df_output=df_output.append(df2014)
del df2014
df2015=migration_sample(2020,2021,sample,state_list)
df_output=df_output.append(df2015)
del df2015
print(df_output.dtypes)
df_output.to_csv('2015-2020_annual_migration_panel_identification_subsample.csv',encoding='utf-8')

# get overall quantiles for all 
quantile=np.arange(0,1.01,0.01)
df=pd.DataFrame(data={'index':quantile})
df['income']=np.nanquantile(df_output[['FIND_DIV_1000']],df['index'])
# df['wealth']=np.nanquantile(df_output[['WEALTH_FINDER_SCORE']],df['index'])
df['housing_value']=np.nanquantile(df_output[['ESTMTD_HOME_VAL_DIV_1000']],df['index'])
df.to_csv('quantile_of_sample.csv',encoding='utf-8',index=False)