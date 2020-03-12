#!/bin/bash

curl -O https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv

# extract header
head -n 1 time_series_19-covid-Confirmed.csv | tr ',' '\n' > foo.txt

# extract counts for Italy
grep Italy time_series_19-covid-Confirmed.csv | tr ',' '\n' > bar.txt

# make a nice count-vs-time file
paste foo.txt bar.txt | grep '/20' | tr '/' ' ' | tr -d -C '[0-9] \t\n' > count_vs_time.txt
rm foo.txt bar.txt
