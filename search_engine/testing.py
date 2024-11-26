from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh.searching import ResultsPage
from whoosh import scoring

from bs4 import BeautifulSoup
from fast_autocomplete import AutoComplete, demo
from fast_autocomplete.misc import *

import os, pickle, re
from anime_search_engine import *

def get_suggested_query(string, last_word_index, whole_string=False):
	if whole_string: last_word_index = 0
	results = autocomplete.search(word=string[last_word_index:], max_cost=3, size=1)
	if not results: return string
	if whole_string:
		result = "' ANDMAYBE '".join(results[0])
		return f"'{result}'"
	else:
		result = results[0][0]
		return string[0:last_word_index]+result

def main:
	query_string = "attack on titan season 2"
	ix = open_dir("./indexdir")
	current_query = QueryParser("title", ix.schema).parse(query_string)
	suggested_string = get_suggested_query(query_string, 0, whole_string=True)


if __name__ == '__main__':
	main()