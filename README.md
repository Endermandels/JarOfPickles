# JarOfPickles


# Activating venv

In Linux and MacOS

>>> source venv/bin/activate

In cmd.exe

>>> venv\Scripts\activate.bat

In PowerShell

>>> venv\Scripts\Activate.ps1


# Deactivating venv

>>> deactivate


# Building page_rank.py

There must be a adjacency matrix csv file in "./sample/adjacency_matrix.csv", where the first line is the list of URLs with the first value being empty. Subsequent lines must start with the URL then 0s and 1s.

Ex.
	,	url1,	url2,	url3
	url1,	1,	0,	1
	url2,	0,	1,	1
	url3,	0,	0,	1


# Running page_rank.py

python3 page_rank.py

Using the above command will create a pickle file, named "page_rank.dat", that stores a dictionary mapping URLs to their PageRank score.


# Building anime_search_engine.py

If the indexdir directory doesn't exist, multiple files must exist to create the index. The "./sample/\_docs_cleaned" and "./sample/\_docs_raw" directories must have a set of regular text and HTML text, respectively. The file in one directory must correspond to the other directory by having the same file names.

A "./sample/url\_map.dat" file must exist, where the file is a pickled dictionary that maps a URL to it's corresponding file name in "./sample/\_docs\_cleaned" and "./sample/\_docs_raw".


# Running anime_search_engine.py

python3 anime_search_engine.py

