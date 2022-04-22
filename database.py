#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 14:49:07 2022

@author: math
"""

import os
import pandas as pd
import datetime as dt
import requests
from bs4 import BeautifulSoup

path_rep = '/media/math/Seagate Backup Plus Drive/films/VO'
path_db = '/data/home/Documents/Coding/Movie_library/library.db'

def import_db(path_db=path_db):
    db = pd.read_csv(path_db, sep=';')
    # db = db.astype({"file": str}, errors='raise') 
    return db

def export_db(db, path_db=path_db):
    db.to_csv(path_or_buf=path_db, sep=';', index=False)

def check_film_in_folder():
    '''check if a film is in a folder, if no ask if create a folder and put it in it.
    '''
    onlyfiles = [f for f in os.listdir(path_rep) if os.path.isfile(os.path.join(path_rep, f))]
    for file in onlyfiles: print(file)
    print(len(onlyfiles), 'not in a folder')
    create_folder = input('put them in folders?[y/N]')
    if create_folder == 'y' or create_folder == 'Y':
        for file in onlyfiles:
            new_folder = os.path.join(path_rep, os.path.splitext(file)[0])
            os.mkdir(new_folder)
            os.rename(os.path.join(path_rep, file), os.path.join(new_folder, file))
            print('moved', file)
    
# check_film_in_folder()

def update_database_files():
    db = import_db()
    count = 0
    for dirpath, dirnames, filenames in os.walk(path_rep):
        for filename in [f for f in filenames if f.endswith((".avi", '.mp4', '.mkv'))]:
            # print(~db['file'].isin([filename]))
            if len(db.loc[db['file'] == filename]) == 0:
                count += 1
                db = db.append({'file':filename,
                                'path_to_file':dirpath,
                                'date_imported':dt.date.today()}, ignore_index=True)
    export_db(db)
    print(count, 'entries added to database')

# update_database_files()

def fill_imdb_url():
    while True:
        db = import_db()
        nadb = db.loc[db['imdb_link'].isna()]
        print(len(nadb), 'IMDB references missing')
        if len(nadb) == 0:
            break
        selected_file = nadb.iloc[0]['file']
        print(selected_file)
        link = input('copy corresponding imdb link: ')
        db.loc[(db['file'] == selected_file), ['imdb_link']] = link
        export_db(db)
        # for index, row in nadb.iterrows():
        #     print(row['file'])
        #     link = input('copy imdb link: ')
    
# fill_imdb_url()  

def imdb_scrapping():
    
    def getTitle(soup):
        try:
            return soup.find('h1', {"data-testid":"hero-title-block__title"}).getText()
        except:
            return 'NaN'
    def getOriginal_title(soup):
        try:
            return soup.find('div', {"data-testid":"hero-title-block__original-title"}).getText().replace('Original title: ' ,'')
        except:
            return 'NaN'
    def getYear(soup):
        try:
            return soup.find('a',{'class':'ipc-link ipc-link--baseAlt ipc-link--inherit-color TitleBlockMetaData__StyledTextLink-sc-12ein40-1 rgaOW'}).getText()
        except:
            return 'NaN'
     
    def getImdbrating(soup):
        try:
            return soup.find('span',{'class':'AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV'}).getText()
        except:
            return 'NaN'
    
    def getDuration(soup):
        try:
            return [f.getText() for f in soup.find_all('div', {"class":"ipc-metadata-list-item__content-container"}) if 'minutes' in f or 'hours' in f or 'minute' in f or 'hour' in f][0]
        except:
            return 'NaN'
    def getImagelink(soup):
        try:
            return [f for f in str(soup.find('div', {"class":"ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"})).split(' ') if 'https' in f and '422' in f ][0]
        except:
            return 'NaN'
    def getCountryorigin(soup):
        try:
            stuff = [f.split('</a>') for f in str(soup.find('section', {"cel_widget_id":"StaticFeature_Details"})).split(' of origin')[1].split('/div')[0].split('rel="">') if '/a' in f]
            stuff = [x for l in stuff for x in l]
            return ','.join([f for f in stuff if '/li' not in f])
        except:
            return 'NaN'
    def getOriginallanguage(soup):
        try:
            stuff = [f.split('</a>') for f in str(soup.find('section', {"cel_widget_id":"StaticFeature_Details"})).split('Language')[1].split('/div')[0].split('rel="">') if '/a' in f]
            stuff = [x for l in stuff for x in l]
            
            return ','.join([f for f in stuff if '/li' not in f])
            
        except:
            return 'NaN'
    def getGenres(soup):
        try:
            return ','.join([f.split('">')[-1] for f in str(soup.find('div', {"data-testid":"genres"})).split('</span>')][:-1])
        except:
            return 'NaN'
    def getSynopsys(soup):
        try:
            return soup.find('span',{'class':'GenresAndPlot__TextContainerBreakpointXS_TO_M-sc-cum89p-0 kHlJyu'}).getText()
        except:
            return 'NaN'
    def getActors(soup):
        try:
            dejy = [f.split('rel="">') for f in str(soup.find('div', {"class":"PrincipalCredits__PrincipalCreditsPanelWideScreen-sc-hdn81t-0 hzbDAm"})).split('Stars</a>')[1].split('</a>')]
            dejy = [x for l in dejy for x in l]
            return ','.join([f for f in dejy if '><' not in f])
        except:
            return 'NaN'
    def getDirector(soup):
        try:
            dejy2 = [f.split('rel="">') for f in str(soup.find('div', {"class":"PrincipalCredits__PrincipalCreditsPanelWideScreen-sc-hdn81t-0 hzbDAm"})).split('Director')[1].split('Writer')[0].split('</a>')]
            dejy2 = [x for l in dejy2 for x in l]
            return ','.join([f for f in dejy2 if '><' not in f])
        except:
            return 'NaN'

    db = import_db()
    to_scrap = db.loc[~db['imdb_link'].isna() & db['title'].isna()]
    print(len(to_scrap), 'titles to scrap')
    if len(to_scrap) > 0:
        for index, row in to_scrap.iterrows():
            print('Scraping', row['file'])
            response=requests.get(row['imdb_link'])
            soup = BeautifulSoup(response.text, 'html.parser')
            
            db.loc[(db['imdb_link'] == row['imdb_link']), ['title']] = getTitle(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['year']] = getYear(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['duration']] = getDuration(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['imdb_rating']] = getImdbrating(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['original_title']] = getOriginal_title(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['image_link']] = getImagelink(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['original_language']] = getOriginallanguage(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['country_origin']] = getCountryorigin(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['genre']] = getGenres(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['synopsys']] = getSynopsys(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['director']] = getDirector(soup)
            db.loc[(db['imdb_link'] == row['imdb_link']), ['actors']] = getActors(soup)
    
        export_db(db)
    
    
# imdb_scrapping()

def check_doublons():
    db = import_db()
    bool_series = db.duplicated(subset='title', keep=False)
    for index, dupl in bool_series.iteritems():
        if dupl == True:
            print('Found duplicated:')
            print(db.iloc[index]['path_to_file'])
        
check_doublons()

def download_posters():
    db = import_db()
    count = 0
    for index, row in db.iterrows():
        if os.path.isfile(os.path.join(row.path_to_file, 'poster.png')) == False:
            response = requests.get(row.image_link, stream = True)
            file = open(os.path.join(row.path_to_file, 'poster.jpg'), "wb")
            file.write(response.content)
            file.close()
            count += 1
    print(count, 'images downloaded')
            
# download_posters()