TZDB analysis : What time is it? Managing Time in the Internet
==============================================================

We have setup this public repository with all the data used in our
analyses and the code used to generate the figures and results
discussed in the paper. We do not require any specialized hardware
setup and once the listed Python package dependencies are installed,
the bash script run_analysis.sh can be executed to reproduce all the
results and figures.

Installation
------------

We recommend Python 3.5 or higher. The python package dependencies are listed under `code/requirements.txt`. To install the dependencies, preferably under a Python virtual environment, run:

```sh
pip install -r code/requirements.txt
```

Usage
-----

To generate all the results and figures from the paper, execute the provided script. The figures are generated under `plots` folder and statistics are written to the standard output.

```
$ ./run_analysis.sh
Processing data from TZDB releases and TZ mailing list archives
Comparing releases...
Processed data written to file data/tz_update_data

Stats for Section 3.1
-----------------------
Number of TZDB releases: 235
Total no. of updates: 2248. Updates to, DST Rules: 1726, Zone Rules: 244, Both: 278
No. of changes affecting, Past : 459, Future: 69, Both: 366
No. of late days: 144, alldelays: 360
Total no. of updates: 2248, Error corrections: 414
Total no. of date ranges affted by Error corrections: 536
 -- No. of date ranges pre-1970: 135
 -- No. of date ranges post-1970: 401

Stats for Section 3.2
-----------------------
No. of months: 335
Total no. of msgs: 17971, Avg. msgs/month: 53.644776119402984
No. of unique contributors: 1791

Data for section 3.3
---------------------
Countries with rule changes during years that exceed the threshold no. of rule changes
(Format - 'country' : no. of rule changes for the year)
---------------------
== 1918 - No. of rules changes: 81 ==
{'Belize': 1, 'Canada': 39, 'Guatemala': 1, 'United States': 40}
== 1942 - No. of rules changes: 59 ==
{'Canada': 25, 'Mexico': 4, 'Puerto Rico': 1, 'United States': 29}
== 1945 - No. of rules changes: 106 ==
{'Canada': 47, 'Cuba': 2, 'Mexico': 1, 'Puerto Rico': 2, 'United States': 54}
== 1967 - No. of rules changes: 28 ==
{'Canada': 3, 'Cuba': 2, 'Dominican Republic': 1, 'United States': 22}
== 1974 - No. of rules changes: 48 ==
{'Belize': 1,
 'Bermuda': 2,
 'Canada': 14,
 'Dominican Republic': 1,
 'Guatemala': 1,
 'Jamaica': 1,
 'United States': 28}
== 1987 - No. of rules changes: 52 ==
{'Bahamas': 1,
 'Bermuda': 1,
 'Canada': 24,
 'El Salvador': 2,
 'Honduras': 2,
 'Mexico': 1,
 'St Pierre & Miquelon': 1,
 'Turks & Caicos Is': 1,
 'United States': 19}
== 2007 - No. of rules changes: 109 ==
{'Bahamas': 2,
 'Bermuda': 2,
 'Canada': 45,
 'Cuba': 1,
 'St Pierre & Miquelon': 2,
 'Turks & Caicos Is': 2,
 'United States': 55}

```

Repository structure
--------------------
Our public repository is organized under four folders.

- The `data` folder contains both the data from TZDB releases and the TZ mailing list archives considered in our analysis. The uncompressed versions of the TZDB releases are under the subfolder tz_data_extracted. The email headers from the archives are under mail_archive_headers and the entire email texts from the archives can be found under mail_archive_body.
- The `utilities` folder contains scripts that can be used to download the mailing list archives and to extract the TZDB release files. This folder also contains the script search_emails.py to perform keyword filtering and manual inspection of the email texts as discussed in Section 3.4.
- The `code` folder contains the scripts used to generate the results and figures, which will be generated under the `plots` folder.

Utilities - usage
-----------------

- `download_archive.py` - Download the TZ mailing list archives. This script downloads both the header files (\*.headers) and email text files (\*.body) under the same folder. The \*.header and \*.body files should be moved to their own folders.
  ```
  $ python utilities/download_archive.py <output folder>
  ```
- `extract_tz.py` - Extract the compressed TZDB release files.
  ```
  $ python utilities/extract_tz.py <input folder> <output folder>
  ```
- `search_emails.py` - Perform keyword searches across the mailist list archive. The script will print the contents of the matching emails to standard output.
  ```
  $ python utilities/search_emails.py <input folder> <search type> <keywords> <optional: N>

  <input folder> - path to folder containing *.body or *.header files.
  <search type> - body or subject
  <keywords> - comma separated list of search keywords
  <N> - optional, terminate after finding N matches
  ```

