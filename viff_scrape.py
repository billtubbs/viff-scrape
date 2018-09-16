# Python script to scrape film information from the
# Vancouver International Film Festival (VIFF) website
# using lxml

import pandas as pd
import numpy as np
import requests
import pickle
from lxml import html

try:
    # For Python 3
    from urllib.parse import urlparse
except ImportError:
    # For Python 2
    from urlparse import urlparse


print("\n -------------- viff_scrape.py --------------\n")

print("Scrape information on this year's films from 'https://www.viff.org'")
year = pd.datetime.now().date().year

# build the lxml tree from the chosen website
# Used this as guide:
# https://docs.python-guide.org/scenarios/scrape/

# Enter the base URL where the A-Z list of films is here (from
# the viff.org home page find the 'Search by Title' option):
start_page = "https://www.viff.org/Online/default.asp?" \
             "doWork::WScontent::loadArticle=Load&BOparam::" \
             "WScontent::loadArticle::" \
             "article_id=D5FA11B0-61FD-4217-AAF7-1FC44D897DA1"

start_page_parse_result = urlparse(start_page)

page = requests.get(start_page_parse_result.geturl())
tree = html.fromstring(page.text)

# Now extract the information we want

# Get a list of URLs to the VIFF pages of each film
film_elements = tree.xpath('/html/body//div[@class="article-' \
                           'container main-article-body"]//div/a')
film_page_links = {
    el.text.strip(): el.attrib['href'] for el in film_elements
}

print("Found links for %d film pages." % len(film_page_links))

film_titles = list(film_page_links.keys())

def get_page_lxml_tree(link,
                       scheme=start_page_parse_result.scheme,
                       netloc=start_page_parse_result.netloc,
                       path=start_page_parse_result.path
                      ):
    """Request page and convert contents into lxml tree"""

    parse_result = urlparse(link)

    if parse_result.netloc is '':
        parse_result = parse_result._replace(netloc=netloc)
    if parse_result.scheme is '':
        parse_result = parse_result._replace(scheme=scheme)
    if start_page_parse_result.path.endswith(parse_result.path):
        parse_result = parse_result._replace(path=path)

    page = requests.get(parse_result.geturl())

    return html.fromstring(page.content)

# Prepare dictionary to collect the film information

year = pd.datetime.now().date().year
data_filename = "viff_data_%d.pickle" % year
try:
    with open("viff_data_%d.pickle" % year, 'rb') as f:
        films = pickle.load(f)
except:
    films = {}
else:
    print("Data from %d films found in data file.")

# Now load each film page and extract the information we are looking for

# Set number of films to parse each time (None for all)
batch = None

already_done = list(films.keys())
total_count = len(films)

print("\nReading information on each film")

for title, link in film_page_links.items():

    if title in already_done:
        continue

    # Request page and convert contents to lxml tree
    film_page_tree = get_page_lxml_tree(link)

    # Get film title (xpath: '//*[@class="movie-title"]')
    try:
        film_title = film_page_tree.find('.//h1[@class="movie-title"]').text.strip()
    except:
        print("WARNING: Getting title for film '%s' failed -> Skipped." % title)
        continue

    # Get film information
    film_info = {}
    try:
        film_information_elements = film_page_tree.find('.//div[@class="movie-information"]').getchildren()
    except:
        print("WARNING: Getting information for film '%s' failed." % title)
    else:
        # Put film information into a dictionary
        labels = ['Director', 'Year:', 'Country of Origin:', 'Running Time:', 'Language:']
        for e in film_information_elements:
            text = e.text_content().strip()

            for label in labels:
                if text[0:len(label)] == label:

                    # remove ':' if there is one
                    if label[-1] == ':':
                        key = label[0:-1]
                    else:
                        key = label

                    film_info[key] = text[text.find(label) + len(label):].strip()

    # Get film description
    try:
        film_description = film_page_tree.find('.//div[@class="movie-description"]').text_content().strip()
    except:
        film_description = None
        print("WARNING: Description for film '%s' missing." % title)

    print(" %4d: %s -> %d info records found." % (total_count, film_title,
                                                  len(film_info)))

    films[film_title] = {
        'Information': film_info,
        'Description': film_description
    }

    total_count += 1
    if batch:
        batch -= 1
        if batch < 1:
            break

print("\nInformation on %d films now acquired." % len(films))

# Now save the film records to an excel file
with open(data_filename, 'wb') as f:
    pickle.dump(films, f)

# Move data into pandas dataframe
columns = set()
data = dict()

for film in films:
    for key in films[film]['Information']:
        columns = columns.union([key])

for column in columns:
    data[column] = []

data['Description'] = []
data['Title'] = []

for film in films:
    data['Title'].append(film)
    for column in columns:
        try:
            data[column].append(films[film]['Information'][column])
        except KeyError:
            data[column].append(np.nan)
    data['Description'].append(films[film]['Description'])

df = pd.DataFrame(data=data)

# Re-order so title column is first
new_columns = list(df.columns.values)
new_columns.remove('Title')
new_columns = ['Title'] + new_columns
df = df[new_columns]

excel_output_filename = "VIFF%d_all.xls" % year
print("Saving results to Excel file '%s'" % excel_output_filename)

# Save to excel
df.to_excel(excel_output_filename)

print("Finished.")



