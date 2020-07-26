
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


# endpoints and params 
base_sec = r'https://www.sec.gov/cgi-bin'


def get_ciks(co_list):
    """
    Get dict of CIKs with co name as key
    
    """
    # Initiatlize dictionary
    co_dict = {co: {'cik': [], 'cik_link': []} for co in co_list} 

    # loop through company names
    for co in co_dict:

        # sleep timer for each loop - randomized
        time.sleep(random.randint(2,4))


        try:

            # get_cik --> start with company name
            cik_res = get_cik(co)
            cik = cik_res[0]
            cik_link = cik_res[1]

            # append results
            co_dict[co]['cik'] = cik
            co_dict[co]['cik_link'] = cik_link


        except:

            # error here, pass
            print('error at ',co, 'pass for now')

    return co_dict


def get_cik(company_name):
    """
    Overview:
    
    Gets cik number for a single company name
    
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
    link = base_sec + '/'+ cik_results[1] if cik_results[1] != 'none' else 'none'

    return cik, link






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
                    'type':'10-K',
                    'dateb':'',
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
    acc_nums = []

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
            acc_num = data[2].text.strip()
            acc_s = acc_num.partition('Acc-no: ')[2]
            acc_nums.append(acc_s[:20])

    return file_types, file_dates, file_num, acc_nums
    
    
    
def get_filings_data(cik_dict):
    """
    Takes a dict of companies (keys) and CIKs (values) and returns filings response data
    
    """
    
    file_features = ['f_type', 'f_date', 'f_num', 'acc_num']

    for co in co_dict:

        # sleep timer for each loop - randomized
        time.sleep(random.randint(2,5))


        if co_dict[co]['cik'] != 'none':

            try:

                # get_filings --> uses cik number
                filing_res = get_filings(co_dict[co]['cik'])

                # unpack response variable
                f_type = filing_res[0]
                f_date = filing_res[1]
                f_num = filing_res[2]
                acc_num = filing_res[3]

                # append result variables
                co_dict[co]['f_type'] = f_type
                co_dict[co]['f_date'] = f_date
                co_dict[co]['f_num'] = f_num
                co_dict[co]['acc_num'] = acc_num

            except:

                # error here, pass for now
                print('error here at ', co, 'pass for now')

        else:

            for feat in file_features:
                co_dict[co][feat] = 'none'

    return co_dict


def filing_landing_tables(co_filing_link):
    """
    Takes a link to the SEC landing page for SPECIFIC filing
    
    """
    co_landing = requests.get(co_filing_link).text
    # Request and Get the html file 
    soup = bs4(co_landing, 'lxml')
    # retrieve all tables from BeautifulSoup object
    co_tables = soup.find_all('table')

    filing_dfs = []
    for t in co_tables:
        """
        Get the rows and table column data for all tables.
        Loop 'manually' rebuilds table data -- stripped and prettified

        """    
        if len(t) > 3:
            table_rows = t.find_all('tr')

            res = []
            for tr in table_rows:
                td = tr.find_all('td')
                row = [tr.text.strip() for tr in td if tr.text.strip()]
                if row:
                    res.append(row)
            df = pd.DataFrame(res)
            filing_dfs.append(df)
            
    return filing_dfs

def filing_homelink(co_name, file_num):
    """
    Takes a string co_name and int number of filing from filings_df and returns the html link
    
    co_name: str of company name from filings_df
    file_num: int of file number in filings_df (Chronological descending)
    
    """
    cik = filings_df['cik'][f'{co_name}']

    # Retrieve SEC Accession No.
    acc = filings_df['acc_num'][f'{co_name}'][file_num]
    acc_raw = acc.replace('-','')

    # Build data url to get html filing landing page
    sec_data_base = 'https://www.sec.gov/Archives/edgar/data/{}/{}/{}-index.htm'
    filing_homelink = sec_data_base.format(cik, acc_raw, acc)

    return filing_homelink

def get_html_path(files_table, wanted_file_type, co, file_num):
    """
    Returns the html file path from wanted file type parameter
    
    files_table: dataframe of landing page table for filing
    wanted_file_type: e.g. '10-K', '10-Q', '8-K'
    co: company name
    
    """
    # file_type
    get_file = wanted_file_type

    # Retrieve SEC Accession No.
    acc = filings_df['acc_num'][f'{co}'][file_num]
    acc_raw = acc.replace('-','')
    
    # Get the html file extension for 10-K
    extension = files_table.apply(lambda x: x[2] if x[1] == get_file else None, axis = 1)

    # filing extension
    html_path = extension[0]
    
    # build url
    sec_file_base = 'https://www.sec.gov/Archives/edgar/data/{}/{}/{}'
    cik_strip = cik.lstrip("0")

    # get url object
    sec_file_resp = requests.get(sec_file_base.format(cik_strip, acc_raw, html_path))
    

    return sec_file_resp.url


def get_filing_tables(soup_tables):
    """
    Scrapes beautiful soup tables, appends to list of tables.
    
    soup: beautiful soup find_all() object
    
    """ 
    
    filing_dfs = []
    for t in soup_tables:
   
        if len(t) > 3:
            table_rows = t.find_all('tr')

            res = []
            for tr in table_rows:
                td = tr.find_all('td')
                row = [tr.text.strip() for tr in td if tr.text.strip()]
                if row:
                    res.append(row)
            df = pd.DataFrame(res)
            filing_dfs.append(df)
        
    print("There are",len(filing_dfs), 'tables in the filing')
    return filing_dfs

# helper function to find table query terms
def table_term_finder(x, search_terms):
    for table_term in x:
        if table_term:
            for sterm in search_terms:
                if str(sterm).lower() in str(table_term).lower():
                    return 'yes'
                
def get_search_tables(search_terms, filing_dfs):
    """
    Arg: search terms list
    
    Returns: 
    List of tables (dataframes) that meet search criteria
    
    """
    interested = []
    for table in filing_dfs:
        # return True if term found
        presence = table.apply(lambda x: table_term_finder(x, search_terms), axis = 1) 

        # append relvant tables from sec filing
        for response in presence:
            if response:
                interested.append(table)
    return interested



def clean_report_table(single_df, new_cols):
    """
    Takes in a single dataframe and cleans, concatenates for export ready df
    
    Params:
    
    single_df: a df (table) from an html sec filing
    new_cols: list of new col names
    
    Returns:
    
    pandas dataframe
    
    """
    
    
    df = single_df.copy()
    
    # column 1 is populated with shifted, isolated dollar symbol, fixed here
    usd_df = df[df[1] == '$']
    no_usd_df = df[df[1] != '$']

    to_drop = []
    for col in usd_df:
        for var in usd_df[col]:
            if '$' in var:
                to_drop.append(col)
                break

    # Drop columns
    usd_df.drop(columns = to_drop, inplace =True)

    # realign columns after drops
    new_cols = [num for num in range(len(usd_df.columns))]
    usd_df.rename(columns = {col:new_col for col, new_col in zip(usd_df.columns, new_cols)},inplace = True)

    # drop all columns with None entirely
    no_usd_df.dropna(axis =1, how ='all', inplace = True)

    # concat new df
    newdf = pd.concat([no_usd_df, usd_df])
    newdf.sort_index(inplace = True)
    
    # define new columns
    newdf.rename(columns = {old:newcol for old,newcol in zip(newdf.columns, newcols)}, inplace = True)
    
    # clean strings, convert to float
    newdf.set_index(0, inplace = True)
    

    return newdf
