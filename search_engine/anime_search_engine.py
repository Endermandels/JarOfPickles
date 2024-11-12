from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh.searching import ResultsPage
from whoosh import scoring

from bs4 import BeautifulSoup

import os, pickle

class SearchEngine(object):

	def __init__(self, index_dir = "./indexdir", page_rank_file = "./page_rank.dat", url_map_file = "./sample/url_map.dat", docs_raw_dir = "./sample/_docs_raw/", docs_cleaned_dir = "./sample/_docs_cleaned/"):
		# File and directory attributes
		self.index_dir = index_dir
		self.page_rank_file = page_rank_file
		self.url_map_file = url_map_file
		self.docs_raw_dir = docs_raw_dir
		self.docs_cleaned_dir = docs_cleaned_dir
		# Whoosh index/scoring attributes
		self.schema = Schema(title=TEXT(stored=True), url = ID(stored=True), content=TEXT(analyzer=StemmingAnalyzer()))
		self.ix = self.__get_indexer()
		self.limit = 10 # Number of results displayed
		self.conj = True
		self.size = self.ix.doc_count()
		self.page_rank = self.__unpickle(page_rank_file)
		assert self.size == len(self.page_rank), "the index and page rank don't match"
		# Whoosh Paging Attributes
		self.searcher = self.ix.searcher(weighting=scoring.FunctionWeighting(self.__custom_scorer))
		self.current_query = None
		self.current_page = 1

	# Returns an existing or new indexer 
	def __get_indexer(self):
		if not os.path.exists(self.index_dir): os.mkdir(self.index_dir)
		if not exists_in(self.index_dir): return self.__create_index()
		else: return open_dir(self.index_dir)

	# Get url map from path file
	def __unpickle(self, path):
		data = None
		with open(path,"rb") as f:
			data = pickle.load(f)
		return data

	# Returns a new indexer with a Whoosh Index
	def __create_index(self):
		ix = create_in(self.index_dir, self.schema)
		writer = ix.writer(limitmb=1024, procs=4, multisegment=True)
		urls = self.__unpickle(self.url_map_file)
		_title = ""
		_url = ""
		_content = ""
		htmlParser = None
		count = 1
		# For each url mapped to a file name
		for u in urls:
			file_name = urls[u]
			# Get the title for the file name
			with open(self.docs_raw_dir+file_name, "r") as html:
				_title = BeautifulSoup(html.read(), "lxml").title.string.strip()
			# Get the text content for the file name
			with open(self.docs_cleaned_dir+file_name, "r") as text:
				_content = text.read()
			print(f"({count}) Indexing {file_name}")
			writer.add_document(title=_title, url=u, content=_content)
			count += 1
		writer.commit()
		return ix

	# Combines page rank and bm25 to be used with scoring.FunctionWeighting
	def __custom_scorer(self, searcher, fieldname, text, matcher):
		url = list(searcher.documents())[matcher.id()]["url"]
		pr = self.page_rank[url]
		bm25 = scoring.BM25F().scorer(searcher, fieldname, text).score(matcher)
		a = 0.5
		b = 0.5
		return a*pr + b*bm25

	def return_page(self, page_num):
		results = {}
		if not self.current_query: 
			print("Submit a query first")
			return results
		
		page_result = self.searcher.search_page(self.current_query, page_num)
		self.current_page = page_result.pagenum
		
		results['total'] = page_result.total
		results['docs'] = []
		
		for result in page_result:
			results['docs'].append({'title': result['title'], 'url': result['url']}) 
		
		return results

	# Prints the page_num page for self.current_query 
	def print_page(self, page_num):
		if not self.current_query: print("Submit a query first")
		else:
			page_result = self.searcher.search_page(self.current_query, page_num)
			self.current_page = page_result.pagenum
			print(f"--------------------\n{page_result.total} RESULTS")
			if page_result.total == 0: print("No results found")
			for result in page_result: print(f"{result["title"]}\n\t\033[94m{result["url"]}\033[0m\n")
			print(f"PAGE {page_result.pagenum} of {page_result.pagecount}")
			print("--------------------")

	# Perform search for a query in the index and print the result
	def submit_query(self, query_string):
		self.current_page = 1
		print(f"\"{query_string}\" WAS SUBMITTED")
		# Construct query based on self.conj
		if self.conj: self.current_query = QueryParser("content", self.ix.schema, group=AndGroup).parse(query_string)
		else: self.current_query = QueryParser("content", self.ix.schema, group=OrGroup).parse(query_string)

	# Prints the page one higher than self.current_page for self.current_query
	def print_next_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page += 1
			self.print_page(self.current_page)

	# Prints the page one lower than self.current_page for self.current_query
	def print_prev_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page -= 1
			self.print_page(self.current_page)

	# Prints page one for self.current_query
	def print_first_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page = 1
			self.print_page(self.current_page)

	# Closes the searcher that is opened during initialization
	def close_searcher(self):
		self.searcher.close()


def main():
	string = "tokyo"
	mySearchEngine = SearchEngine()
	mySearchEngine.print_first_page()
	mySearchEngine.submit_query(string)
	mySearchEngine.print_first_page()
	mySearchEngine.print_next_page()
	mySearchEngine.close_searcher()

if __name__ == "__main__":
	main()