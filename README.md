# SEC Scraper Tool

### Table of Contents

1. [Purpose](#motivation)
2. [File Descriptions](#files)

## Project Purpose<a name="motivation"></a>

The purpose of this repository is to scrape the SEC Edgar filings for a given list of company names.

The names are first searched within the CIK code database, then the CIK code is used as primary key to navigate within the SEC Edgar site.


## File Descriptions <a name="files"></a>

.py files: files containing functions for import within the sec_scraper.ipynb file

.ipynb: Jupyter Notebook for running the program

