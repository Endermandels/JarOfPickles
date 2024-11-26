import os
import sys
import inspect

# Move CWD to parent dir to have access to search_engine
# Code from https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from flask import Flask, render_template, request
from search_engine.anime_search_engine import SearchEngine


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Inspired by Pretty Printed on YouTube: https://youtu.be/PWEl1ysbPAY?si=eKrzQqsts-G-TvkK
@app.route('/search')
def search():
    q = request.args.get('q')
    print(q)
    
    results = []
    
    if q and mySearchEngine:
        mySearchEngine.submit_query(q)
        results = mySearchEngine.return_page(1)['docs']
       
    return render_template("search_results.html", results=results)
    
def start_app():
    global mySearchEngine
    dir = 'search_engine'
    mySearchEngine = SearchEngine(
        index_dir=f'../{dir}/indexdir/'
        , page_rank_file=f'../{dir}/startup_files/page_rank.dat'
        , titles_file=f'../{dir}/startup_files/titles.dat'
        , synonyms_file=f'../{dir}/startup_files/synonyms.dat'
        , url_map_file=f'../{dir}/sample/url_map.dat'
        , docs_raw_dir=f'../{dir}/sample/_docs_raw/'
        , docs_cleaned_dir=f'../{dir}/sample/_docs_cleaned/')
    app.run(debug=True)
    mySearchEngine.close_searcher()

if __name__ == '__main__':
    start_app()