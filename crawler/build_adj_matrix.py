from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pickle
import sys
import re


def filter_links(href: str):
	"""
	Filter invalid or unhelpful links.
 
    Params
        href: The link to filter
    
    Returns
        Whether the link should be kept
	"""
	if href:
		# Do not include Random, as it could cause problems while storing the urls
		if re.compile('/wiki/Special:Random').search(href):
			return False
		if re.compile('#').search(href):
			return False
		if re.compile('Category:').search(href):
			return False
		if re.compile(':Citation').search(href):
			return False
		return True
	return False

def build_adj_dict(url_map: dict[str, str], save_fn: str) -> dict[str, dict[str, int]]:
    """
    Builds a dictionary mapping urls to a dictionary which maps outgoing links to their count
    Structures the adjacency dictionary as follows:
        {url: {outgoing_link: count}}
    
    Params
        url_map: Dictionary of urls to document names
        save_fn: File name to save adjacency dict to
    
    Returns
        Adjacency dictionary
    """
    adj_dict = {}
    
    for url, docFN in url_map.items():
        with open('./_docs_raw/' + docFN, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            
            links = {}
            for link in soup.find_all('a', href=filter_links):
                try:
                    full_url = urljoin(url, link['href'])
                    
                    if full_url in links:
                        links[full_url] += 1
                    else:
                        links[full_url] = 1
                except Exception as e:
                    print('Error occurred while joining url:', e)
                    if input('continue? (Y/n) ').lower() == 'n':
                        with open(save_fn, 'wb') as file:
                            pickle.dump(adj_dict, file)
                        return adj_dict
            
            adj_dict[url] = links
            
    with open(save_fn, 'wb') as file:
        pickle.dump(adj_dict, file)

    return adj_dict

def build_adj_matrix(adj_dict: dict[str, dict[str, int]], save_fn: str) -> pd.DataFrame:
    """
    Creates an adjacency matrix for a list of URLs.
    
    Params
        adj_dict: Adjacency dictionary
        save_fn:  File name to save adjacency matrix to
    
    Returns
        DataFrame containing adjacency matrix
    """
    urls = adj_dict.keys()
    n = len(urls)
    adjacency_matrix = np.zeros((n, n), dtype=np.uint8)

    for i, url in enumerate(urls):
        links = adj_dict[url]
        for j, target_url in enumerate(urls):
            if target_url in links and i != j:
                adjacency_matrix[i][j] = links[target_url]

    df = pd.DataFrame(adjacency_matrix, index=urls, columns=urls)
    
    with open(save_fn, 'wb') as file:
        pickle.dump(df, file)
        
    return df
    
def main():
    """
    Builds either an adjacency dictionary or an adjacency matrix.
    The adjacency dict must exist in order to build the adjacency matrix.
    
    Run with the -d option to build the adjacency dictionary.
    Run with the -m option to build the adjacency matrix.
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            with open('url_map.dat', 'rb') as file:
                print('building adjacency dictionary...')
                build_adj_dict(pickle.load(file), 'adj_dict.dat')
            print('finished')
        elif sys.argv[1] == '-m':
            with open('adj_dict.dat', 'rb') as file:
                print('building adjacency matrix...')
                build_adj_matrix(pickle.load(file), 'adj_matrix.dat')
            print('finished')
        else:
            print('usage: python3 build_adj_matrix.py <-d | -m>')
    else:
        print('usage: python3 build_adj_matrix.py <-d | -m>')

if __name__ == '__main__':
    main()