
# OVERVIEW: functions get CIK codes for a company name and lookup
# ...associated SEC filings - form D.

# imports for program
# BeautifulSoup is only third-party package

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs4
import random
import time
import json
import numpy as np
import re
import os


# initial endpoints and params 
base_sec_cgi = r'https://www.sec.gov/cgi-bin'
base_sec = r'https://www.sec.gov/cgi-bin'

# get_cik()

def get_cik(company_name):
    """
    Overview:
    
    Gets cik number for a given company name
    
    Params:
    
    name --> company name
    
    Returns:
    
    cik -- cik number
    link -- sec base link + cik number attached
    
    """
    # endpoint and cik params for get method
    cik_endpoint = r'https://www.sec.gov/cgi-bin/cik_lookup'
    params_cik = {'company': f'{company_name}'}

    cik_results = get_atags(get_tables(cik_endpoint, params = params_cik))

    cik = cik_results[0]
    link = base_sec_cgi + '/'+ cik_results[1] if cik_results[1] != 'none' else 'none'

    return cik, link



def get_filings(cik):
    """
    Overview:
    Takes in CIK, returns filings data
    
    Params:
    CIK --> cik number
    
    """
    
    # run function, get data table
    tables = get_edgar_tables(cik)


    # master storage for data per each filing
    file_types = []
    file_dates = []
    file_num = []
    # file_link = []

    for row in tables[0].find_all('tr'):
        data = row.find_all('td')

        if len(data) > 1:

            # unpack data

            # append file data to master storage
            filing_type = data[0].text.strip()
            file_types.append(filing_type)
            filing_date = data[3].text.strip()
            file_dates.append(filing_date)
            filing_num = data[4].text.strip()
            file_num.append(filing_num)

    return file_types, file_dates, file_num





def get_atags(tables):
    """
    Overview: 
    gets atags for CIK lookup results
    
    params:
    bs4 tables --> results of bs4.find_all('table')
    
    """

    # only one table, grab first
    tdata = tables[0]

    # pull a tags
    atag = [data.find_all('a') for data in tdata]

    # atag[0] holds relevant tags list

    if len(atag[0])>1:
        cik = atag[0][0].text.strip()
        link = atag[0][0]['href']
        
        return cik, link
    else:
        return 'none', 'none'
    


def get_tables(endpoint, params):
    """
    Overview:
    Extracts all tables from url's html, returns a list
    
    Params:
    url
    
    """
    
    html = requests.get(endpoint, params = params).text
    
    # html = requests.get(html_url).text
    # initiate bs object
    soup = bs4(html,'lxml')
    # 25 total tables on FAA site
    tables = soup.find_all('table')
    
    return tables

def get_edgar_tables(cik):
    """
    Overview:
    Extracts all tables from sec cik page, returns a list
    
    Params:
    cik --> cik number
    
    """
    # url endpoint for browsing sec edgar
    edgar_endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"
    
    # f string cik num from parameters
    params_edgar = {'action':'getcompany',
                    'CIK':f'{cik}',
                    'type':'',
                    'dateb':'20140101',
                    'owner':'exclude',
                    'start':'',
                    'output':'',
                    'count':'100'
                   }
    
    html = requests.get(url = edgar_endpoint, params = params_edgar).text
    
    # html = requests.get(html_url).text
    # initiate bs object
    soup = bs4(html,'lxml')
    # 25 total tables on FAA site
    tables = soup.find_all('table', class_='tableFile2')
    
    return tables




def check_formd(ftype_list):
    """
    Overview:
    Takes a list of file types and checks for Form D types
    
    Params:
    List of file types
    
    Returns:
    'Yes' or 'No' string
    
    """

    if type(ftype_list) == list:
    
        d_list = [f for f in ftype_list if f == 'D' or 'D/A']

        if len(d_list) > 0:
    
            return 'Yes'
        else:
            return 'No'

    elif type(ftype_list) == str:

        if ftype_list == 'D' or 'D/A':

            return 'Yes'
        else:
            return 'No'

    else:
        return 'No'

        
def likely_private(co, filings_df):
    """
    Checks row in dataframe for a company likely to be private
    
    Returns 'yes' or 'no'
    
    """
    df = filings_df.copy()
    
    if df.at[co, 'cik'] == 'none':
        return 'Yes'
    elif '10-Q' in df.at[co, 'f_type'] or '10-K' in df.at[co, 'f_type']:
        return 'No'
    else:
        return 'Yes'
        
        
    