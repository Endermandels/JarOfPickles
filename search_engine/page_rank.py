import numpy as np
import pickle
import pandas as pd
from scipy import sparse
import gc

# Returns a page rank vector for a given SciPy transition matrix
# (no added leap probability),number of links, damping factor, and epsilon threshold
def __page_rank(L, n, d=0.85, epsilon = 0.0001):
	p_new = np.full(n, 1/n)
	while True:
		p_old = p_new
		p_new = L.dot(p_new) + ((1-d)/n)
		if not np.any(abs(p_old-p_new) >= epsilon): return p_new

# Returns a SciPy transition matrix of a SciPy adjacency matrix
def __adjacency_to_transition_matrix(adjMatrix, d=0.85):
	s = adjMatrix.sum(axis=1)
	return (d*(adjMatrix/s)).T

# Pickles a dictionary mapping url to PageRank score for a Pandas DataFrame
def __pickle_page_rank(df_path, d=0.85, epsilon = 0.0001):
	df = pd.read_pickle(df_path)
	url_to_pr = {}
	url_array = list(df.columns)
	matrix = sparse.csr_matrix(df.values)

	df = None # Python can garbage collect the DataFrame

	matrix = __adjacency_to_transition_matrix(matrix, d)

	page_rank = __page_rank(matrix, matrix.shape[0], d, epsilon)

	for i in range(matrix.shape[0]):
		url_to_pr[url_array[i]] = float(page_rank[i])

	with open("page_rank.dat","wb") as f:
		pickle.dump(url_to_pr,f)

__pickle_page_rank("../crawler/adj_matrix.dat")

