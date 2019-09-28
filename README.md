# viff-scrape

Two python scripts to collect information on the current films listed on the Vancouver International Film Festival's website (www.viff.org) and save them as an excel spreadsheet.

* [viff_scrape.py](viff_scrape.py) - uses lxml but does not acquire film screening times
* [viff_scrape2.py](viff_scrape2.py) - acquires film screening times and venue information using [Selenium](https://selenium-python.readthedocs.io) web driver.

## Installation

Clone this repository to your machine.

From the command-line:
```
git clone https://github.com/billtubbs/viff-scrape.git
```

Navigate to the directory.

```
cd viff-scrape
```


## Dependencies

Before you can run `viff_scrape.py` you will need to install Python version 3 and the following packages:

```
conda install urllib, requests, lxml, numpy, pandas, pickle, xlwt
```

To run `viff_scrape2.py` you will also need:

```
conda install selenium
```


## Usage

Both scripts gather the following information on each film:

1. Title
2. Running Time
3. Year
4. Director
5. Country of Origin
6. Language
7. Description

The second script also captures:

8. Screening date 1
9. Screening venue 1
10. Screening date 2
11. Screening venue 2
12. ...etc.

The reason the first script does not capture the screening times is that they are produced with a java script widget.

Typical usage from command-line:

```
$ python viff_scrape.py

 -------------- viff_scrape.py --------------

Scrape information on this year's films from 'https://www.viff.org'
Found links for 355 film pages.

Reading information on each film
    0: 14 Apples -> 5 info records found.
    1: 3 Faces -> 5 info records found.
    2: 7A -> 4 info records found.
    3: Acres -> 4 info records found.
    4: Ãga -> 5 info records found.
    5: Akeda (The Binding) -> 5 info records found.
...

   75: Dovlatov -> 5 info records found.
   76: A Dreaming House -> 4 info records found.
WARNING: Description for film 'Dreaming Under Capitalism' missing.
...

  354: You Don't Know Me -> 5 info records found.

Information on 355 films now acquired.
Results saved to file 'viff_data_2018.pickle'.
Saving results to Excel file 'VIFF2018_all.xls'
Finished.
```
