from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh import scoring

from bs4 import BeautifulSoup

import os, pickle

class SearchEngine(object):

	def __init__(self):
		self.schema = Schema(title=TEXT(stored=True), url = ID(stored=True), content=TEXT(analyzer=StemmingAnalyzer()))
		self.ix = self.__get_indexer("./indexdir")
		self.limit = 10 # Number of results displayed
		self.conj = True
		self.size = self.ix.doc_count()
		self.page_rank = self.__unpickle("./page_rank.dat")
		assert self.size == len(self.page_rank), "the index and page rank don't match"

	# Returns an existing or new indexer 
	def __get_indexer(self, path):
		if not os.path.exists(path): os.mkdir(path)
		if not exists_in(path): return self.__create_index(path)
		else: return open_dir(path)

	# Get url map from path file
	def __unpickle(self, path):
		data = None;
		with open(path,"rb") as f:
			data = pickle.load(f)
		return data

	# Returns a new indexer with a Whoosh Index
	def __create_index(self, path):
		ix = create_in(path, self.schema)
		writer = ix.writer(limitmb=1024, procs=4, multisegment=True)
		urls = self.__unpickle("./sample/url_map.dat")
		_title = ""
		_url = ""
		_content = ""
		htmlParser = None;
		count = 1
		# For each url mapped to a file name
		for u in urls:
			file_name = urls[u]
			# Get the title for the file name
			with open("./sample/_docs_raw/"+file_name, "r") as html:
				_title = BeautifulSoup(html.read(), "lxml").title.string.strip()
			# Get the text content for the file name
			with open("./sample/_docs_cleaned/"+file_name, "r") as text:
				_content = text.read()
			print(f"({count}) Indexing {file_name}")
			writer.add_document(title=_title, url=u, content=_content)
			count += 1
		writer.commit()
		return ix

	# Print the search results
	def __print_result(self, results_obj):
		print(results_obj.top_n)
		print(f"--------------------\n{len(results_obj)} RESULTS")
		if len(results_obj) == 0: print("No results found")
		for result in results_obj: print(f"{result["title"]}\n\t\033[94m{result["url"]}\033[0m\n")
		print("--------------------")

	# Combines page rank and bm25 to be used with scoring.FunctionWeighting
	def __custom_scorer(self, searcher, fieldname, text, matcher):
		html = list(searcher.documents())[matcher.id()]["url"]
		pr = self.page_rank[html]
		bm25 = scoring.BM25F().scorer(searcher, fieldname, text).score(matcher)
		a = 0.5
		b = 0.5
		return a*pr + b*bm25

	# Perform search for a query in the index and print the result
	def query_search(self, query_string):
		print(f"SEARCHING: {query_string}")
		with self.ix.searcher(weighting=scoring.FunctionWeighting(self.__custom_scorer)) as searcher:
			# Construct query based on self.conj
			if self.conj: query = QueryParser("content", self.ix.schema, group=AndGroup).parse(query_string)
			else: query = QueryParser("content", self.ix.schema, group=OrGroup).parse(query_string)
			results = searcher.search(query, limit = self.limit)
			self.__print_result(results)
		

def main():
	string = "anime"
	mySearchEngine = SearchEngine()
	mySearchEngine.query_search(string)
	

if __name__ == "__main__":
	main()