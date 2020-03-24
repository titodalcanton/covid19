#!/bin/bash

curl -o raw.txt https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv

# extract header
head -n 1 raw.txt | tr ',' '\n' > header.txt

# extract counts for Italy
grep '^,Italy' raw.txt | tr ',' '\n' > bar.txt

# make a nice count-vs-time file
paste header.txt bar.txt | grep '/20' | tr '/' ' ' | tr -d -C '[0-9] \t\n' > count_vs_time_it.txt

# extract counts for France
grep '^,France' raw.txt | tr ',' '\n' > bar.txt

# make a nice count-vs-time file
paste header.txt bar.txt | grep '/20' | tr '/' ' ' | tr -d -C '[0-9] \t\n' > count_vs_time_fr.txt

rm header.txt bar.txt
