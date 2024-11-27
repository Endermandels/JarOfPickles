from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh.searching import ResultsPage
from whoosh import scoring

from bs4 import BeautifulSoup
from fast_autocomplete import AutoComplete, demo
from fast_autocomplete.misc import *

import os, pickle, re, json
from anime_search_engine import *


def main():
	with open("./startup_files/synonyms.dat", "rb") as f:
		x = pickle.load(f)

		print(x)

		with open("./startup_files/synonyms.json", "w") as output:
			json.dump(x, output, indent=4)


if __name__ == '__main__':
	main()