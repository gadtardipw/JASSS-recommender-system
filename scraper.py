import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from datetime import datetime


# settings for scraper loop 
starting_volume = 1
ending_volume = 26

starting_issue = 1
ending_issue = 4

starting_number = 1
ending_number = 30

headers = {'User-Agent': 'Gadtardi Wongkaren (psygw7@nottingham.ac.uk) (BSc dissertation) (An Improved Scientific Paper Recommender System for the Journal of Artificial Societies and Simulation (JASSS.org) Papers)'}

# whitespace cleaner for meta tags
def clean_whitespace(text):
    return re.sub(r'\s+', ' ', text.strip())

# author names cleaner
def clean_author_names(author_string):
    # remove any leading or trailing whitespaces and newlines
    author_string = author_string.strip()
    
    # replace multiple whitespaces with a single space
    author_string = re.sub(r'\s+', ' ', author_string)
    
    # replace " and " with a comma, only if "and" is surrounded by word boundaries
    author_string = re.sub(r'\b\s+and\s+\b', ', ', author_string)
    
    # split the names at the commas, and then remove any extra spaces around the names
    author_list = [name.strip() for name in author_string.split(',')]
    
    # join the cleaned names back together with commas
    cleaned_names = ', '.join(author_list)

    return cleaned_names

# date tag cleaner
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return datetime.strptime(date_str, "%d-%b-%y").strftime("%Y-%m-%d")

# write-to-dataset
with open('jasss_dataset.csv', mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter='|')
    writer.writerow(['ID', 'Title', 'URI', 'Publish_date', 'Authors', 'Abstract', 'Keywords'])


    # paper id incrementor
    paper_id = 1
    failed_scrapes = 0

    # URL looping mechanism
    for volume in range(starting_volume, ending_volume+1):
     for issue in range(starting_issue, ending_issue+1):
        for number in range(starting_number, ending_number+1):
            try:
                url = f'https://www.jasss.org/{volume}/{issue}/{number}.html'
            
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # meta tag extractors
                title = clean_whitespace((soup.find("meta", {"name" : "DC.Title"}))['content'])
                uri = (soup.find("meta", {"name" : "DC.Identifier.URI"}) or soup.find("meta", {"name" : "DC.Identifier"}))['content']
                publish_date_raw = parse_date(clean_whitespace((soup.find("meta", {"name" : "DC.Issued"}) or soup.find("meta", {"name" : "DC.Date"}))['content']))
                publish_date = parse_date(publish_date_raw)
                authors = soup.find("meta", {"name" : "DC.Creator"})['content']
                authors = clean_author_names(authors)
                abstract = clean_whitespace((soup.find("meta", {"name" : "DC.Abstract"}) or soup.find("meta", {"name" : "DC.Description"}))['content'])
                keywords = clean_whitespace((soup.find("meta", {"name" : "DC.Subject"}))['content'])

                writer.writerow([paper_id, title, uri, publish_date, authors, abstract, keywords])
                
                print(f"Data written for paper {paper_id}, URI {uri}")
                paper_id += 1
                # set figure here for delay between requests
                time.sleep(3)

            # exception handler
            except Exception as e:
                    print(f"Error encountered for paper: volume {volume}, issue {issue}, paper number {number}, URI {uri} : {e}")
                    failed_scrapes += 1
                    continue

print("Data collection is complete.")
print(f"Number of successfully scraped papers: {paper_id-1}")
print(f"Number of scrapes failed: {failed_scrapes}")