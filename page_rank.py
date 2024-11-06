import numpy as np
import csv, pickle

# Returns a page rank vector for a given transition matrix, number
# of links, damping factor, and epsilon threshold
def __page_rank(L, n, d=0.85, epsilon = 0.0001):
	p_new = np.full(n, 1/n)
	while True:
		lp = np.dot(L, p_new)
		p_old = p_new
		p_new = d*lp + ((1-d)/n)
		if not np.any(abs(p_old-p_new) >= epsilon): return p_new
	
# Returns a transition matrix of an adjacency matrix
def __adjacency_to_transition_matrix(adjMatrix):
	row_count = 0
	for row in adjMatrix:
		one_count = np.count_nonzero(row)
		np.copyto(adjMatrix[row_count], row/one_count)
		row_count += 1
	return np.transpose(adjMatrix)

# Reads a given csv file and returns a matrix
def __csv_to_matrix(path):
	matrix = []
	with open(path, "r" ,newline = '') as file:
		csv_file = csv.reader(file)
		csv_file.__next__()
		for lines in csv_file:
			matrix.append(lines[1:])
	return np.array(matrix,dtype=float)

# Returns a dictionary mapping url to PageRank score
def __pickle_page_rank(csv_path, d=0.85, epsilon = 0.0001):
	url_to_pr = {}
	url_array = []
	with open(csv_path, "r" ,newline = '') as file:
		csv_file = csv.reader(file)
		url_array = csv_file.__next__()[1:]
	matrix = __csv_to_matrix(csv_path)
	matrix = __adjacency_to_transition_matrix(matrix)
	page_rank = __page_rank(matrix, matrix.shape[0], d, epsilon)
	for i in range(matrix.shape[0]):
		url_to_pr[url_array[i]] = float(page_rank[i])
	with open("page_rank.dat","wb") as f:
		pickle.dump(url_to_pr,f)

__pickle_page_rank("./sample/adjacency_matrix.csv")