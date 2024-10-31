import numpy as np
import csv

# Returns a page rank vector for a given transition matrix, number
# of links, damping factor, and epsilon threshold
def page_rank(L, n, d=0.85, epsilon = 0.0001):
	p_new = np.full(n, 1/n)
	while True:
		lp = np.dot(L, p_new)
		p_old = p_new
		p_new = d*lp + ((1-d)/n)
		if not np.any(abs(p_old-p_new) >= epsilon): return p_new
	
# Returns a transition matrix of an adjacency matrix
def adjacency_to_transition_matrix(adjMatrix):
	row_count = 0
	for row in adjMatrix:
		one_count = np.count_nonzero(row)
		np.copyto(adjMatrix[row_count], row/one_count)
		row_count += 1
	return np.transpose(adjMatrix)

# Reads a given csv file and returns a matrix
def csv_to_matrix(path):
	matrix = []
	with open(path, "r" ,newline = '') as file:
		csv_file = csv.reader(file)
		csv_file.__next__()
		for lines in csv_file:
			matrix.append(lines[1:])
	return np.array(matrix,dtype=float)

def main():
	matrix = csv_to_matrix("./sample/adjacency_matrix.csv")
	matrix = adjacency_to_transition_matrix(matrix)
	pr = page_rank(matrix, matrix.shape[0])
	print(pr)
	
if __name__ == "__main__":
	main()