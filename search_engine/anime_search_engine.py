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

# This function is needed because the scoring.FunctionWeighting.FunctionScorer
# needs a max_quality function.
def max_quality(self):
	return 9999

class SearchEngine(object):

	def __init__(self, index_dir = "./indexdir", page_rank_file = "./page_rank.dat", url_map_file = "./sample/url_map.dat", docs_raw_dir = "./sample/_docs_raw/", docs_cleaned_dir = "./sample/_docs_cleaned/", title_file = "./titles.dat", synonym_file="./synonym.dat", debug = False):
		# File and directory attributes
		self.index_dir = index_dir
		self.page_rank_file = page_rank_file
		self.url_map_file = url_map_file
		self.docs_raw_dir = docs_raw_dir
		self.docs_cleaned_dir = docs_cleaned_dir
		self.title_file = title_file
		self.synonym_file = synonym_file
		# Whoosh index/scoring attributes
		self.title_dic = {}
		self.synonym_dic = {}
		self.schema = Schema(title=TEXT(stored=True), url = ID(stored=True), content=TEXT(analyzer=StemmingAnalyzer()))
		self.ix = self.__get_indexer()
		self.limit = 10 # Number of results displayed
		self.conj = True
		self.size = self.ix.doc_count()
		self.page_rank = self.__unpickle(page_rank_file)
		assert self.size == len(self.page_rank), "the index and page rank don't match"
		# Whoosh Paging Attributes
		custom_weighting = scoring.FunctionWeighting(self.__custom_scorer)
		custom_weighting.FunctionScorer.max_quality = max_quality
		self.searcher = self.ix.searcher(weighting=custom_weighting)
		self.document_list = list(self.searcher.documents())
		self.current_query = None
		self.current_page = 1
		self.debug = debug
		self.autocomplete = AutoComplete(words=self.title_dic, synonyms=self.synonym_dic)

	# Returns an existing or new indexer 
	def __get_indexer(self):
		if not os.path.exists(self.index_dir): os.mkdir(self.index_dir)
		if not exists_in(self.index_dir): return self.__create_index()
		else:
			 # Only unpickle titles if we don't index
			self.title_dic = self.__unpickle(self.title_file)
			self.synonym_dic = self.__unpickle(self.synonym_file)
			return open_dir(self.index_dir)

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
		_content = ""
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
		url = self.document_list[matcher.id()]["url"]
		pr = self.page_rank[url]
		bm25 = scoring.BM25F().scorer(searcher, fieldname, text).score(matcher)
		a = 100000 # Most PageRank is 1E-6 place
		b = 1.5
		return a*pr + b*bm25

	# Returns a dictionary representation of a page result
	def return_page(self, page_num):
		results = {}
		if not self.current_query: 
			print("Submit a query first")
			return results

		if page_num < 1: page_num = 1
		
		page_result = self.searcher.search_page(self.current_query, page_num)
		self.current_page = page_result.pagenum
		
		results['total'] = page_result.total
		results['docs'] = []
		
		for result in page_result:
			results['docs'].append({'title': result['title'], 'url': result['url']}) 
		
		return results

	# Prints the page_num page for self.current_query 
	def print_page(self, result_dic):
		print(f"--------------------\n{result_dic["total"]} RESULTS")
		if result_dic["total"] == 0: print("No results found")
		for result in result_dic["docs"]: print(f'{result["title"]}\n\t\033[94m{result["url"]}\033[0m\n')
		print(f"PAGE {self.current_page}")
		print("--------------------")

	# Perform search for a query in the index and print the result
	def submit_query(self, query_string):
		self.current_page = 1
		print(f"\"{query_string}\" WAS SUBMITTED")
		# Construct query based on self.conj
		if self.conj: self.current_query = QueryParser("title", self.ix.schema, group=AndGroup).parse(query_string)
		else: self.current_query = QueryParser("title", self.ix.schema, group=OrGroup).parse(query_string)

	# Returns an object with page result information for a page one higher than self.current_page for self.current_query
	def get_next_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page += 1
			page_result = self.return_page(self.current_page)
			if self.debug: self.print_page(page_result)
			return page_result

	#  Returns an object with page result information for a page one lower than self.current_page for self.current_query
	def get_prev_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page -= 1
			page_result = self.return_page(self.current_page)
			if self.debug: self.print_page(page_result)
			return page_result

	#  Returns an object with page result information for page one for self.current_query
	def get_first_page(self):
		if not self.current_query: print("Submit a query first")
		else:
			self.current_page = 1
			page_result = self.return_page(self.current_page)
			if self.debug: self.print_page(page_result)
			return page_result

	# Closes the searcher that is opened during initialization
	def close_searcher(self):
		self.searcher.close()

	def get_suggested_query(self, string, last_word_index, whole_string=False):
		if whole_string: last_word_index = 0
		results = self.autocomplete.search(word=string[last_word_index:], max_cost=3, size=1)
		if not results: return string
		if whole_string:
			result = "' ANDMAYBE '".join(results[0])
			return f"'{result}'"
		else:
			result = results[0][0]
			return string[0:last_word_index]+result


	# Terminal demo modified from fast_autocomplete.demo
	def demo(self):
		word_list = []
		start_of_words = [0]
		cursor_index = 0
		suggested_query = ""
		use_autocomplete = True
		last_result = None
		if self.debug: print("Demo started. Type something (exit with ctrl+c)")
		while (True):
			pressed = read_single_keypress()
			# Exit with ctrl+c
			if pressed == '\x03': break # \x03 is ctrl+c
			# Backspace character is pressed
			elif pressed == '\x7f':
			    if word_list:
			    	cursor_index -= 1
			    	char = word_list.pop()
			    	# Update the start_of_words if a word is deleted
			    	if (word_list and word_list[-1] == ' ' and char != ' '): start_of_words.pop()
			# Tab character is pressed, use auto-complete
			elif pressed == '\x09':
				# Create a list of indices to update start_of_words if the result has space characters
				new_string_array = list(suggested_query[start_of_words[-1]:])
				indices = [i for i, x in enumerate(new_string_array) if x == ' ']
				if indices:
					new_indices = []
					for i in range(len(indices)):
						if i+1 < len(indices) and indices[i+1] == indices[i]+1: continue
						new_indices.append(indices[i])
					if indices[-1] == len(new_string_array)-1: new_indices.pop()
					indices = [x+1+start_of_words[-1] for x in indices]
				# Replace the last word with the result
				word_list = word_list[0:start_of_words[-1]] + new_string_array
				cursor_index = start_of_words[-1]+len(new_string_array)
				start_of_words += indices
			else:
				if word_list and word_list[-1] == ' ' and pressed != ' ': start_of_words.append(cursor_index)
				word_list.append(pressed)
				cursor_index += 1

			print(chr(27) + "[2J")
			query = ''.join(word_list)
			print(query+"_")
			print("Last word:", start_of_words[-1])
			print("Current cursor:", cursor_index)
			print(''.join(word_list[start_of_words[-1]:]))
			new_suggested_query = self.get_suggested_query(query, start_of_words[-1], whole_string=True)
			if (True):
				suggested_query = new_suggested_query
				if use_autocomplete: self.submit_query(f"({suggested_query}) OR ({query})")
				else: self.submit_query(query)
				last_result = self.get_first_page()
			else:
				print(f"SUBMITTED {suggested_query} ({query})")
				print(self.print_page(last_result))


def main():
	string = "faefafesf"
	print("initializing search engine...")
	mySearchEngine = SearchEngine(
		debug=True,
		url_map_file="./new_sample/url_map.dat",
		docs_raw_dir ="./new_sample/_docs_raw/",
		docs_cleaned_dir="./new_sample/_docs_cleaned/")
	print("starting demo...")
	mySearchEngine.demo()
	mySearchEngine.close_searcher()

if __name__ == "__main__":
	main()
