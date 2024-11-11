from gensim.models import Word2Vec
from gensim.models import Phrases
import pickle

class create_word_2_vec_corpus(object):
	def __init__(self, url_map_file = "./sample/url_map.dat", docs_cleaned_dir = "./sample/_docs_cleaned/"):
		self.url_map_file = url_map_file
		self.docs_cleaned_dir = docs_cleaned_dir

	# Get url map from path file
	def __unpickle(self, path):
		data = None;
		with open(path, "rb") as f:
			data = pickle.load(f)
		return data

	def __iter__(self):
		urls = self.__unpickle(self.url_map_file)
		for u in urls:
			file_name = urls[u]
			with open(self.docs_cleaned_dir+file_name, "r") as text:
				content = [word.lower() for word in text.read().split()]
				yield content

def main():
	corpus = create_word_2_vec_corpus()
	model = Word2Vec(sentences=corpus)
	model.save("word2vec.model")
	sims = model.wv.most_similar("tokyo")
	for sim in sims:
		print(sim[0])

if __name__ == '__main__':
	main()
