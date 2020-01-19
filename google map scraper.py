from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import pandas as pd
import time
import requests
import os
import sqlite3
from selenium import webdriver
import urllib
from selenium.webdriver.common.action_chains import ActionChains
from urllib.request import urlopen as uReq
import pickle
from  geopy.geocoders import Nominatim
all_data=[]

def get_lang_lat(st):
    lang = ''
    lat = ''
    flag = 0
    for i in st:
        if flag == 3:
            break

        if i == '@':
            flag = 1
            continue

        if i == ',':
            flag += 1
            continue

        if flag == 1:
            lang += i
        if flag == 2:
            lat += i

    return   lang, lat

chrome_options = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="C:\chromedriver_win32\chromedriver.exe" )
driver.set_window_position(10000, 0)

driver.get('https://www.google.com/maps')
time.sleep(3)
driver.find_element_by_xpath('/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form/div/div[3]/div/input[1]').send_keys('rio de janeiro bar')
driver.find_element_by_xpath('/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/button').click()


while(1):
    time.sleep(5)
    cc=1
    # inner page...
    while(1):
        try:
            if cc>39:
                break
            data = []
            time.sleep(2)
            print(cc)
            f=0
            while(1):
                try:
                    f+=1
                    driver.find_element_by_xpath(
                        '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[4]/div[1]/div[{}]'.format(
                            cc)).click()


                    break
                except:
                    if f==50:
                        break
                    pass
            cc += 2
            time.sleep(5)

            # business name
            try:
                temp = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[2]/div[1]/div[1]/h1').text
                data.append(temp)
            except:
                data.append('')

            # address
            try:
                temp = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[9]/div/div[1]/span[3]/span[3]').text
                data.append(temp)
            except:
                data.append('')

            # Neighborhood

            try:
                temp = str(data[1]).split(',')
                temp2 = str(temp[1]).split('-')
                data.append(temp2[-1])

            except:
                data.append('')

            # Region

            try:
                temp = str(data[1]).split(',')
                temp2 = str(temp[2]).split('-')
                data.append(temp2[0])

            except:
                data.append('')

            # rating
            try:
                temp = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span').text
                data.append(temp)
            except:
                data.append('')

            # lang & lat
            try:
                url = driver.current_url
                x, y = get_lang_lat(url)
                data.append(x)
                data.append(y)
            except:
                data.append('')
                data.append('')


            # website
            try:
                temp = driver.find_elements_by_class_name('section-info-text')
                f=0
                for i in temp:
                    if '.com' in i.text or '.net' in i.text or '.org' in i.text :
                        if 'facebook' not in i.text:
                            data.append(i.text)
                        else:
                            data.append('')
                        f=1
                        break
                if f==0:
                    data.append('')
            except:
                data.append('')


            # mobile
            try:
                temp = driver.find_elements_by_class_name('section-info-text')
                f=0
                for i in temp:
                    if '+' == str(i.text)[0]:
                        data.append(i.text)
                        f=1
                        break
                if f==0:
                    data.append('')
            except:
                data.append('')

            # category

            try:
                temp = driver.find_element_by_xpath(
                '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button').text
                data.append(temp)
            except:
                data.append('')


            # hours
            c=0
            while(1):
               try:
                   if c>20:
                       data.append('')
                       break
                   c += 1

                   temp = driver.find_element_by_xpath(
                       '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[{}]'.format(c)).text

                   if 'Closed' in temp or 'Opens' in temp or 'বন্ধ' in temp:
                        driver.find_element_by_xpath(
                           '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[{}]'.format(c)).click()
                        time.sleep(2)
                        temp2 = driver.find_element_by_xpath(
                            '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[{}]'.format(c)).text
                        temp = str(temp2).split('\n')
                        temp = temp[1:]
                        st = '{\n'
                        for i in range(0, int(len(temp) / 2)):

                            new = temp[i * 2 + 1].split('–')

                            if len(new) == 2:
                                s1 = '"{}" : '.format(str(temp[i * 2][:3]))
                                s2 = ('"Open": "{}", "Close" : "{}"'.format(new[0], new[1]))
                                final = s1 + '{ ' + s2 + ' },\n'
                                st += (final)
                            else:
                                s1 = '"{}" : '.format(str(new[0][:3]))
                                final = s1 + '{ ' + '"Closed"' + ' },\n'
                                st += (final)

                        st = st[:-2]
                        st += '\n}'

                        data.append(st)
                        break
               except:
                   pass

            # images
            try:
               temp = driver.find_element_by_xpath(
    '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[1]/div[1]/button/img').get_attribute('src')
               data.append(temp)
            except:
               data.append('')

            print(data)
            if (len(data)) ==12:
                all_data.append(data)


            # back to the search result page

            driver.find_element_by_xpath('/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/button').click()
            time.sleep(2)
        except Exception as e:

            break


    # save in each page

    col = ['Name', 'address', 'Neighborhood', 'region', 'Rating', 'Latitude', 'Longitude'
        , 'website', 'Phone', 'Tags', 'Hours', 'Image']

    df = pd.DataFrame(all_data, columns=col)
    df.to_excel('data.xlsx')

    # next page
    try:

        driver.find_element_by_xpath(
            '/html/body/jsl/div[3]/div[9]/div[9]/div/div[1]/div/div/div[4]/div[2]/div/div[1]/div/button[2]').click()
        time.sleep(5)
    except:
        break


col =[ 'Name',	'address' ,'Neighborhood',	'region',	'Rating', 'Latitude',	'Longitude'
       ,'website',	'Phone','Tags','Hours',	'Image']

df = pd.DataFrame(all_data, columns=col)
df.to_excel('data.xlsx')