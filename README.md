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

Create a new search engine with SearchEngine()

Submit a query with SearchEngine.submit_query("some_string")

Print the result for the query with  
	SearchEngine.print_page(page_num)  
	SearchEngine.print_first_page()  
	SearchEngine.print_next_page()  
	SearchEngine.print_prev_page()  

You must close the searcher after with SearchEngine.close_searcher()

Ex.  
	string = "tokyo"  
	mySearchEngine = SearchEngine()  
	mySearchEngine.submit_query(string)  
	mySearchEngine.print_first_page()  
	mySearchEngine.print_next_page()  
	mySearchEngine.close_searcher()  


# Running anime_search_engine.py

python3 anime_search_engine.py

