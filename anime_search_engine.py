from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from bs4 import BeautifulSoup
from whoosh.qparser import QueryParser, OrGroup, AndGroup
import os, pickle

class SearchEngine(object):

	def __init__(self):
		self.schema = Schema(title=TEXT(stored=True), url = ID(stored=True), content=TEXT(analyzer=StemmingAnalyzer()))
		self.ix = None
		if not os.path.exists("./indexdir"): os.mkdir("./indexdir")
		if not exists_in("./indexdir"): self.create_index()
		else: self.ix = open_dir("./indexdir")
		self.limit = 10 # Number of results displayed
		self.conj = True


	# Get url map from path file
	def get_url_map(self, path):
		data = None;
		with open(path,"rb") as f:
			data = pickle.load(f)
		return data

	# Initializes self.ix with a Whoosh Index
	def create_index(self):
		self.ix = create_in("indexdir", self.schema)
		writer = self.ix.writer(limitmb=1024, procs=4, multisegment=True)
		urls = self.get_url_map("./sample/url_map.dat")
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

	# Print the search results
	def print_result(self, results_obj):
		print(f"--------------------\n{len(results_obj)} RESULTS")
		if len(results_obj) == 0: print("No results found")
		for result in results_obj: print(f"{result["title"]}\n\t\033[94m{result["url"]}\033[0m\n")
		print("--------------------")

	# Perform search for a query in the index and print the result
	def query_search(self, query_string):
		print(f"SEARCHING: {query_string}")
		with self.ix.searcher() as searcher:
			# Construct query based on self.conj
			if self.conj: query = QueryParser("content", self.ix.schema, group=AndGroup).parse(query_string)
			else: query = QueryParser("content", self.ix.schema, group=OrGroup).parse(query_string)
			results = searcher.search(query, limit = self.limit)
			self.print_result(results)
		

def main():
	string = "animes"
	mySearchEngine = SearchEngine()
	mySearchEngine.query_search(string)
	

if __name__ == "__main__":
	main()