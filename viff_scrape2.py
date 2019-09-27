# Python script to scrape film information from the
# Vancouver International Film Festival (VIFF) website
# using Selenium

import pandas as pd
import numpy as np
import requests
import pickle
from selenium import webdriver

try:
    # For Python 3
    from urllib.parse import urlparse
except ImportError:
    # For Python 2
    from urlparse import urlparse

print("\n -------------- viff_scrape2.py --------------\n")

print("Scrape information on this year's films from 'https://www.viff.org'")
year = pd.datetime.now().date().year

print("Launching Selenium web-page driver...")
driver = webdriver.Safari()  # Other options include Chrome, Firefox

# Enter the base URL where the A-Z list of films is here (from
# the viff.org home page find the 'Search by Title' option):
start_page_url = "https://viff.org/Online/default.asp?BOparam::"\
                 "WScontent::loadArticle::permalink=2019-filmindex&BOparam::"\
                 "WScontent::loadArticle::context_id="

print("Opening Viff film list web-page...")
# Open webpage in driver
driver.get(start_page_url)

# Now extract the information we want

# Get a list of URLs to the VIFF pages of each film
xp = '/html/body//div[@class="article-container main-article-body"]//div/a'
film_link_elements = driver.find_elements_by_xpath(xp)
film_page_links = [
    {'text': el.text.strip(), "href": el.get_attribute('href')}
    for el in film_link_elements
]
print("Found links for %d film pages." % len(film_page_links))

start_page_parse_result = urlparse(start_page_url)

def convert_link_to_url(link, scheme=start_page_parse_result.scheme,
                        netloc=start_page_parse_result.netloc,
                        path=start_page_parse_result.path):
    """Converts a relative link such as 'default.asp' into an absolute url
    such as 'https://www.viff.org/Online/default.asp' using the scheme,
    netloc, and path specified."""

    parse_result = urlparse(link)

    if parse_result.netloc is '':
        parse_result = parse_result._replace(netloc=netloc)
    if parse_result.scheme is '':
        parse_result = parse_result._replace(scheme=scheme)
    if start_page_parse_result.path.endswith(parse_result.path):
        parse_result = parse_result._replace(path=path)

    return parse_result.geturl()

def get_film_details(driver, max_screenings=5):
    """Reads film information from Selenium web-driver."""

    # Get movie title
    xp = './/h1[@class="movie-title"]'
    try:
        film_title = driver.find_element_by_xpath(xp).text.strip()
    except:
        print("WARNING: Title for film '%s' not found on page " \
              "-> skipped." % film_title)
        return None

    # Get film information
    film_info = {}
    xp = './/div[@class="movie-information"]/*'
    try:
        film_info_elements = driver.find_elements_by_xpath(xp)
    except:
        print("WARNING: Getting information for film '%s' failed." % film_title)
    else:
        # Put film information into a dictionary
        labels = ['Director', 'Year:', 'Country of Origin:',
                  'Running Time:', 'Language:']
        for e in film_info_elements:
            text = e.text.strip()

            for label in labels:
                if text[0:len(label)] == label:

                    # remove ':' if there is one
                    if label[-1] == ':':
                        key = label[0:-1]
                    else:
                        key = label

                    film_info[key] = text[text.find(label) + len(label):].strip()

    # Get film description
    xp = '//div[@class="movie-description"]'
    try:
        film_description = driver.find_element_by_xpath(xp).text.strip()
    except:
        film_description = None
        print("WARNING: Description for film '%s' missing." % film_title)

    # Get screening times
    xp = '//div[@class="movie-tickets"]/div[@name="avWidget"]' \
         '//div[@class="item-description result-box-item-details"]'
    search_result_elements = driver.find_elements_by_xpath(xp)
    screenings = []

    if len(search_result_elements) > max_screenings:
        print("WARNING: Film '%s' has more than %d screening times."
              "Only 4 will be saved" % (film_title, max_screenings))

    for element in search_result_elements:

        start_date_string = element.find_element_by_class_name('item-start-date') \
                            .find_element_by_class_name('start-date').text
        venue = element.find_element_by_class_name('item-venue').text

        screenings.append({
                'Start date': pd.to_datetime(start_date_string),
                'Venue': venue
            })

    film_details = {
        'Title': film_title,
        'Information': film_info,
        'Description': film_description,
        'Screenings': screenings
    }

    return film_details

# Prepare dictionary to collect the film information
data_filename = "viff_data_%d_2.pickle" % year
try:
    with open(data_filename, 'rb') as f:
        films = pickle.load(f)
except:
    films = {}
else:
    print("Data from %d films found in data file." % len(films))

# ----------------- MAIN LOOP -----------------
print("loading each film page to extract information...")

# Set number of films to parse each time (None for all)
batch = None

already_done = list(films.keys())
total_count = len(films)
max_screenings = 3

film_page_links[2]
for page_link in film_page_links:

    title, link = page_link['text'], page_link['href']

    # Skip if already in films dictionary
    if title in already_done:
        continue

    # Convert link to a complete url
    page_url = convert_link_to_url(link)

    # Get film information
    driver.get(page_url)
    film_details = get_film_details(driver)

    if film_details is None:
        # Skip this film
        continue

    if film_details['Title'] != title:
        print("WARNING: Title for film '%s' does not match link." % title)

    films[title] = film_details
    print(" %4d: %s" % (total_count, film_details['Title']))

    total_count += 1
    if batch:
        batch -= 1
        if batch < 1:
            break

print("\nInformation on %d films now acquired." % len(films))

# Now save the film records to an excel file
with open(data_filename, 'wb') as f:
    pickle.dump(films, f)
print("Results saved to file '%s'." % data_filename)

print("Closing Selenium web-page driver...")
driver.close()

# Move data into pandas dataframe
info_cols = set()
data = dict()

for film in films:
    for key in films[film]['Information']:
        info_cols = info_cols.union([key])

max_screenings = max([len(details['Screenings']) for
                      details in films.values()])

date_cols = set(["Screening date %d" % (i + 1) for i in range(max_screenings)])
venue_cols = set(["Screening venue %d" % (i + 1) for i in range(max_screenings)])

# Add an empty list to dictionary for each series expected
for column in info_cols.union(date_cols).union(venue_cols):
    data[column] = []
data['Description'] = []
data['Title'] = []

for film in films:
    data['Title'].append(film)
    for col in info_cols:
        try:
            data[col].append(films[film]['Information'][col])
        except KeyError:
            data[col].append(np.nan)
    data['Description'].append(films[film]['Description'])
    for i, cols in enumerate(zip(date_cols, venue_cols)):
        try:
            data[cols[0]].append(films[film]['Screenings'][i]['Start date'])
            data[cols[1]].append(films[film]['Screenings'][i]['Venue'])
        except IndexError:
            data[cols[0]].append(np.nan)
            data[cols[1]].append(np.nan)

# Dataframe from data
df = pd.DataFrame(data=data)

# Re-order so title column is first
new_columns = list(df.columns.values)
new_columns.remove('Title')
new_columns = ['Title'] + new_columns
df = df[new_columns]

excel_output_filename = "VIFF%d_all_with_dates.xls" % year
print("Saving results to Excel file '%s'" % excel_output_filename)

# Save to excel
df.to_excel(excel_output_filename)

print("Finished.")







