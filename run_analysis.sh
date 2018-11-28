#!/bin/bash

# README:
# This script will preprocess TZDB and TZ mailing list archive data
# and run the analyses discussed in the paper.
# The plots will be generated under the plots directory.
# Various statistics will be printed to standart output.
#
# It is assumed that Python 3.5 or above is available and all the
# required Python packages from code/requirements.txt have been
# installed.

echo "Processing data from TZDB releases and TZ mailing list archives"
python code/categorize_updates.py data/tz_data_extracted/ data/mail_archive_headers/ data/tz_update_data

echo ""
python code/get_db_update_stats.py data/tz_update_data data/tz_data_extracted data/mail_archive_headers/
echo ""
python code/get_contributor_stats.py data/mail_archive_headers/ data/tz_data_extracted
echo ""
python code/plot_histogram.py data/tz_data_extracted/tzdata2018e/northamerica
