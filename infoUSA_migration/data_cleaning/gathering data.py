# download detailed infoUSA datasets into 100 large csv files to decrease future cleaning time

import pandas as pd
import numpy as np
import os
import string
import time as time

pd.set_option('display.max_columns', None)

# preinput
# state code
df_state=pd.read_csv('D:/combined data/us-state-ansi-fips.csv')
dict_state=dict(zip(df_state['stab'][:],df_state['code'][:]))
# print(dict_state['AL'])
# print(dict_state)

# LOCATION_TYPE
dict_location={'M':1,'N':2,'R':3,'S':4,'T':5,'U':6}

# HEAD_HH_AGE_CODE
dict_age=dict(zip(string.ascii_uppercase[:13],(22,27,32,37,42,47,52,57,62,72,67,72,77)))

# Ethnicity_Code_1
df_ethnicity=pd.read_csv('D:/combined data/IU_ethnicity_codes_from_Davis_Berlind_for_python.csv')
dict_race=dict(zip(df_ethnicity['subcode'][:],df_ethnicity['race code'][:]))
dict_race['00']=0
dict_race['NA']=0
# print(dict_race)

# HOUSEHOLDSTATUS
dict_hs={'F':1,'S':2,'I':3,'M':4}

# other
df_county=pd.read_csv('D:/combined data/county_geo.csv')


# get cloud based infoUSA dataset location
inputdir = "//oit-nas-fe11.oit.duke.edu/ssri-infousa/derived set/2006"
filenames=os.listdir(inputdir)
# print(filenames)
# print(len(filenames))


# generate divided list so that 5 degit zipcode can be classified into 100 files so that "10" 
# file contains all households data within zip code where the first two degit is 10
generated_list=np.arange(0,100,1)
lista=[str(i) for i in generated_list]
# # divided_list[:10]='0'+divided_list[:10]
for i in range(10):
    lista[i]='0'+lista[i]
# print(lista)


divided_list=[]
for i in lista:
    print(i)
    divided_sublist = []
    for j in filenames:
        if 'copy' not in j:
            if 'txt' in j:
                j_split = j.split('_')
                if i == j_split[3][:2]:
                    # print(j)
                    divided_sublist.append(j)
    divided_list.append(divided_sublist)

# generate infoUSA data based on given list name, you can modify how it generate by changing
# first two number in np.arange(1,20,1)
for i in np.arange(1,100,1):
    list = divided_list[i]
    print(i)
    print(list[:10])
    if len(list)!=0:
        # print(list)
        list = sorted(list)
        print(list)
        count = 0
        df_empty = pd.DataFrame()
        # start = time.time()
        for file in list:
            df = pd.read_csv(inputdir + '/' + file, sep='\t',encoding='ISO-8859-1')
            savename = file.split('_')
            # print(df)

            # only include subset of the data that is useful
            df = df[['FAMILYID', 'HEAD_HH_AGE_CODE', 'PRIMARY_FAMILY_IND', 'ESTMTD_HOME_VAL_DIV_1000',
                     'FIND_DIV_1000', 'OWNER_RENTER_STATUS', 'STATE', 'GE_ALS_COUNTY_CODE_2010', 'ZIP',
                     'Ethnicity_Code_1',
                     'CITY', 'VACANT', 'LENGTH_OF_RESIDENCE', 'CHILDREN_IND', 'CHILDRENHHCOUNT',
                     'GE_LATITUDE_2010', 'GE_LONGITUDE_2010', 'GE_CENSUS_LEVEL_2010', 'GE_ALS_CENSUS_TRACT_2010'
                , 'GE_ALS_CENSUS_BG_2010',
                     'LOCATIONID','HOUSE_NUM','STREET_NAME','STREET_SUFFIX','UNIT_TYPE']]

            # only include primary family
            df=df[df['PRIMARY_FAMILY_IND'] == 1].copy()
            df.drop(['PRIMARY_FAMILY_IND'],axis=1,inplace=True)

            # change code
            df['STATE'] = df['STATE'].replace(dict_state)
            df['HEAD_HH_AGE_CODE'] = df['HEAD_HH_AGE_CODE'].replace(dict_age)

            # df['HOUSEHOLDSTATUS'] = df['HOUSEHOLDSTATUS'].replace(0, np.nan)
            # df['HOUSEHOLDSTATUS'] = df['HOUSEHOLDSTATUS'].fillna(value='NA')
            # df['HOUSEHOLDSTATUS'] = df['HOUSEHOLDSTATUS'].replace(dict_hs)

            df['Ethnicity_Code_1'] = df['Ethnicity_Code_1'].replace(0, np.nan)
            df['Ethnicity_Code_1'] = df['Ethnicity_Code_1'].fillna(value='NA')
            df['Ethnicity_Code_1'] = df['Ethnicity_Code_1'].replace(dict_race)

            # fill county data assuming all householods in each zip code remains in the same county
            df['GE_ALS_COUNTY_CODE_2010'] = df['GE_ALS_COUNTY_CODE_2010'].replace(0, np.nan)
            
            county = df['GE_ALS_COUNTY_CODE_2010'].mode()[0]
            df['GE_ALS_COUNTY_CODE_2010'] = df['GE_ALS_COUNTY_CODE_2010'].fillna(county)

            df['Ethnicity_Code_1'] = df['Ethnicity_Code_1'].fillna(value=0)

            # other
            df['year'] = int(savename[5][:4])

            df_empty = df_empty.append(df)
            count = count + 1
            print(count)
            # print(file)

        end = time.time()
        # print(df_empty.dtypes)
        # print(start - end)
        df_empty.to_csv(lista[i] + '_' + savename[5][:4] + '.csv',encoding='utf-8')
