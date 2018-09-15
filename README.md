# viff-scrape

Python script to collect information on the current films listed on the Vancouver International Film Festival's website (www.viff.org) and save them as an excel spreadhseet.

* [viff_scrape.py](viff_scrape.py)

Gathers the following information on each film:
1. Title	
2. Running Time	
3. Year	
4. Director	
5. Country of Origin	
6. Language	
7. Description

Unfortunately, it does not acquire the screening dates/times.  This turned out to be a java script widget, so that would have to be done differently (e.g. with Selenium).

Typical operation:

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
