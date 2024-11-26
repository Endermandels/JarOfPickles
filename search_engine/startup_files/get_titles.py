from bs4 import BeautifulSoup
from threading import Thread
import pickle, re, os

title_dic = {}

# Removes clutter from titles
def clean_title(title):
	global synonym_dic
	title = title.lower().strip()
	title = re.sub(r"(\s*-\s*myanimelist\.net\s*)$", "", title)
	title = re.sub(r"(\s*\|\s*.+)$", "", title)

	match = re.search(r"(\s*\(.+\)\s*)$", title)
	if (match):
		title = re.sub(r"(\s*\(.+\)\s*)$", "", title)
		# synonym_dic[title] = [match.group().strip(" ()")]
	return title

# Unpickles pickle files
def __unpickle(path):
	data = None
	with open(path,"rb") as f:
		data = pickle.load(f)
	return data

# Adds titles for a given start and stop range for a list of urls.
# urls is a dictionary mapping urls to file names.
# url_list is a list of urls. docs_raw_dir is the path to _docs_raw
def get_titles(start, stop, urls, url_list, docs_raw_dir):
	_title = ""
	count = 1
	global title_dic

	for u in url_list[start:stop-1]:
		file_name = urls[u]
		# Get the title for the file name
		with open(docs_raw_dir+file_name, "r") as html:
			_title = BeautifulSoup(html.read(), "lxml").title.string.strip()
			cleaned_title = clean_title(_title)
			title_dic[cleaned_title] = {}

		print(f"({count}) got {cleaned_title}")
		count += 1

# Pickles a dictionary mapping titles to an empty dictionary
def main():
	path = os.path.dirname(os.path.realpath(__file__))
	os.chdir(path)

	thread_num = 8
	threads = [None]*thread_num
	ranges = [0]*thread_num
	urls = __unpickle('../new_sample/url_map.dat')
	url_list = list(urls.keys())
	total = len(urls)-1
	global title_dic
	global synonym_dic
	for i in range(thread_num):
		if i == 0:
			ranges[0] = total//thread_num
		else:
			ranges[i] = ranges[i-1]+total//thread_num
		if i == thread_num-1:
			ranges[i] += total-ranges[i]

	for i in range(thread_num):
		start = 0;
		end = 0;
		if i == 0:
			start = 0
		else:
			start = ranges[i-1]
		end = ranges[i]
		threads[i] = Thread(target = get_titles, args = (start, end, urls, url_list,'./new_sample/_docs_raw/'))
	
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()

	with open("titles.dat","wb") as f:
		pickle.dump(title_dic,f)


if __name__ == '__main__':
	main()