import requests

import regex as re

import sys

import time

import textwrap

import pandas as pd

import numpy as np

from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait

import time
import os

pd.set_option('display.max_columns', None)

# open chrome that enables constant reopenin
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

driver.maximize_window()

# find text and return missing if xpath does not exist
def find_with_missing(command, by='xpath'):
    try:

        element = driver.find_element(by, command)

        return element.text

    except:

        return np.nan

# clean string to numeric value
def clean_tax_string(string):
    for value in [",", "$", "Unpaid", "Paid "]:

        if value in string:
            string = string.replace(value, "")

    try:

        return float(string)

    except:

        return string


# scrap tax data by chunks and reopen the driver after 20 iterations to avoid memory issues
def tax_data_folio(folio, driver, k):
    k += 1

    url = 'https://miamidade.county-taxes.com/public/search/property_tax'

    if driver.current_url != url:
        print('new')

        driver.get(url)

    driver.switch_to.default_content()
    time.sleep(1)

    df_mid = pd.DataFrame()

    # type folio
    try:

        type_box = WebDriverWait(driver, 30).until(

            EC.presence_of_element_located(

                #                 (By.XPATH, '/html/body/div[2]/div[2]/div/main/div/div/section[1]/div[2]/div/div/div/div[1]/input'))
                (By.XPATH, '/html/body/div/div/div[2]/div/div/div/div/section[1]/div[2]/div/div[1]/input'))
        )

        type_box.send_keys(folio)

        time.sleep(1)

        type_box.send_keys(Keys.ENTER)

        # test if multiple addresses exists and generate multiple datasets if multiple addresses exists
        # if so, enter the matched address.
        try:
            iframe = WebDriverWait(driver, 60).until(
        
                EC.presence_of_element_located(
        
                    (By.XPATH, "/html/body/div/div/div[2]/div/div[2]/iframe"))
            )
        except:
            df_mid.loc[1, 'folio'] = folio
        
            df_mid.loc[1, 'missing_input'] = 1
        
            print('issues with multiple input  ' + folio)
        
            if driver.find_element(By.XPATH,
                                   '/html/body/div/div/div[2]/div/div/div/div/section[1]/div[1]/h5').text == 'Search':
                for i in np.arange(1, 5):
                    print(i)
                    folio_add = WebDriverWait(driver, 20).until(
        
                        EC.presence_of_element_located(
                            (By.XPATH, '/html/body/div/div/div[2]/div/div/div/section/div[2]/div/div[' + str(
                                i) + ']/div/div[1]/div[1]/div/span'))
                    )
                    folio_add = folio_add.text
        
                    if folio_add == folio:
                        button = WebDriverWait(driver, 10).until(
        
                            EC.presence_of_element_located((By.XPATH,
                                                            '/html/body/div/div/div[2]/div/div/div/section/div[2]/div/div[' + str(
                                                                i) + ']/div/div[2]/button'))
        
                        )
        
                        button.click()
        
                        break
                    else:
                        print(folio_add)

        # collect owner name
        try:
            driver.switch_to.default_content()
            time.sleep(0.5)
            iframe = WebDriverWait(driver, 60).until(

                EC.presence_of_element_located(

                    (By.XPATH, "/html/body/div/div/div[2]/div/div[2]/iframe"))

            )
            driver.switch_to.frame(iframe)
            owner = driver.find_element(By.XPATH, '/html/body/div[2]/main/section/div[2]/div[2]/div[1]/div[2]/div')

            owner = owner.text

            time.sleep(0.5)

            # extract data for 2013-2023 if available

            for i in np.arange(1, 36, 1):

                try:
                    if "Bill" in find_with_missing(

                            '//*[@id="bill-history-content"]/table/tbody[' + str(i) + ']/tr[1]/th/a[1]'):
                        # time

                        df_mid.loc[i, 'time'] = find_with_missing(

                            '//*[@id="bill-history-content"]/table/tbody[' + str(i) + ']/tr[1]/td[3]/time')

                        # unpaid

                        df_mid.loc[i, 'unpaid'] = clean_tax_string(find_with_missing(

                            '//*[@id="bill-history-content"]/table/tbody[' + str(i) + ']/tr[1]/td[1]'))

                        # paid

                        df_mid.loc[i, 'paid'] = clean_tax_string(find_with_missing(

                            '//*[@id="bill-history-content"]/table/tbody[' + str(i) + ']/tr[1]/td[2]'))

                        # year

                        df_mid.loc[i, 'year'] = find_with_missing(

                            '//*[@id="bill-history-content"]/table/tbody[' + str(i) + ']/tr[1]/th/a[1]')

                except:

                    pass

            df_mid['folio'] = folio

            df_mid['owner'] = owner

            # to get detailed ownership data, get in to detailed page to collect data for all years when Miami has the data.
            # run data for all year in year list
            for year in year_list:

                df_mid_mid = df_mid[df_mid['year'].str.contains(str(year))]

                i = 0
                for index, row in df_mid_mid.iterrows():
                    if i < 1:
                        i += 1
                        try:
                            driver.switch_to.default_content()

                            iframe2 = WebDriverWait(driver, 60).until(

                                EC.presence_of_element_located(

                                    (By.XPATH, "/html/body/div/div/div[2]/div/div[2]/iframe"))

                            )
                            driver.switch_to.frame(iframe2)
                            time.sleep(0.1)

                            button = WebDriverWait(driver, 60).until(

                                EC.presence_of_element_located((By.LINK_TEXT, df_mid.loc[index, 'year']))

                            )

                            button.click()

                            time.sleep(0.5)

                            driver.switch_to.default_content()

                            try:
                                iframe = WebDriverWait(driver, 60).until(

                                    EC.presence_of_element_located(

                                        (By.XPATH, "/html/body/div/div/div[2]/div/div[2]/iframe"))

                                )
                                driver.switch_to.frame(iframe)

                                # find data table and divide to list to get detailed tax information
                                time.sleep(0.1)

                                table_text = driver.find_element(By.XPATH, '/html/body/div[2]/main/section/div[4]')
                                total = find_with_missing(
                                    '/html/body/div[2]/main/section/div[3]/div[7]/div/table/tbody[2]/tr/td[2]')
                                table_text = table_text.text.split('\n')

                                #                                 print(table_text)
                                driver.switch_to.default_content()

                                # find tax, exemption, assessed value in table

                                if 'Assessed value:' in table_text:
                                    df_mid.loc[index, 'assessed'] = clean_tax_string(table_text[

                                                                                         table_text.index(
                                                                                             'Assessed value:',

                                                                                             0,

                                                                                             len(table_text)) + 1])

                                if 'School assessed value:' in table_text:
                                    df_mid.loc[index, 'school_assessed'] = clean_tax_string(table_text[

                                                                                                table_text.index(

                                                                                                    'School assessed value:',

                                                                                                    0,

                                                                                                    len(
                                                                                                        table_text)) + 1])

                                if 'ADDL HOMESTEAD' in table_text:
                                    df_mid.loc[index, 'homestead_add'] = clean_tax_string(table_text[

                                                                                              table_text.index(

                                                                                                  'ADDL HOMESTEAD', 0,

                                                                                                  len(table_text)) + 1])

                                if 'Owner:' in table_text:
                                    df_mid.loc[index, 'owner_detail'] = clean_tax_string(table_text[

                                                                                             table_text.index('Owner:',

                                                                                                              0,

                                                                                                              len(
                                                                                                                  table_text)) + 1])

                                if 'HOMESTEAD' in table_text:
                                    df_mid.loc[index, 'homestead'] = clean_tax_string(table_text[

                                                                                          table_text.index('HOMESTEAD',
                                                                                                           0,

                                                                                                           len(
                                                                                                               table_text)) + 1])

                                if 'Total tax:' in table_text:
                                    df_mid.loc[index, 'tax_total'] = clean_tax_string(table_text[

                                                                                          table_text.index('Total tax:',
                                                                                                           0,

                                                                                                           len(
                                                                                                               table_text)) + 1])

                                df_mid.loc[index,'total']=clean_tax_string(total)

                                time.sleep(1)

                                # return

                                driver.back()

                            except:

                                # if get into the detailed page

                                if "bills/" in driver.current_url:

                                    df_mid.loc[index, 'missing_detailed_information'] = 1

                                    time.sleep(0.2 + np.random.normal(0, 0.1))

                                    driver.back()

                                else:

                                    break

                        except:

                            df_mid.loc[index, 'missing_clickable_detail'] = 1


        except:  # pass if no folio related property tax data is found

            df_mid.loc[1, 'folio'] = folio

            df_mid.loc[1, 'missing_owner_name'] = 1

            print('couldnt find folio place for_' + folio)



    except:  # if could not find place to type in folio

        df_mid.loc[1, 'folio'] = folio

        df_mid.loc[1, 'missing_property'] = 1

        print('didnt wait enough time_' + folio)



    # open a new driver if something wrong

    finally:

        try:

            driver.get(url)

        except:

            driver = webdriver.Chrome(options=options)

            driver.maximize_window()

    return [df_mid, driver, k]

# # test data output
# folio='01-0201-020-1130'
# [df_mid, driver, k] = tax_data_folio(folio, driver, 2)
# print(df_mid)

df=pd.read_csv('web_scraping_use.csv')
folio_list = df['folio_str'].unique().tolist()

print(len(df))

print(len(folio_list))

# generate subdataframe

chunks = [folio_list[x:x + 100] for x in range(0, len(folio_list), 100)]

print(len(chunks))
dir=os.getcwd()
print(dir.split('\\')[6])
start=int(dir.split('\\')[6])+10*int(dir.split('\\')[5])
print(start)

# automatically scrap data by name of the folder the file is currently in
for i in np.arange(start*20, len(chunks), 1):
    print(i)

    chunk = chunks[i]

    # record time for each section
    start = time.time()

    print(len(chunk))
    print(chunk)

    df_output = pd.DataFrame()

    n = 0
    k = 0

    for folio in chunk:
        n += 1

        # open new driver if k>20
        if k > 20:
            driver.quit()
            time.sleep(0.3)

            driver = webdriver.Chrome(options=options)

            k = 0
        # base url

        print(n, k)

        [df_mid, driver, k] = tax_data_folio(folio, driver, k)
        # print(df_mid)


        df_output = pd.concat([df_output, df_mid])
        print(time.time()-start)

    end = time.time()

    print(i)

    print((end - start) / 60)

    df_output.to_csv('web_scripting_tax_allyear_' + str(i) + '.csv', index=False)
