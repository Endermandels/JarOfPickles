from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Code by Pretty Printed on YouTube: https://youtu.be/PWEl1ysbPAY?si=eKrzQqsts-G-TvkK

@app.route('/search')
def search():
    q = request.args.get('q')
    print(q)
    
    # TODO: DELETE
    docs = [
        ['hello', 'world', 'it', 'is', 'cool']
        , ['hello', 'world', 'it', 'is', 'nice']
        , ['hello', 'world', 'it', 'is', 'awesome']
        , ['hello', 'world', 'it', 'is', 'cheese']
    ]
    
    results = []
    
    if q:
        # User has a query
        # Search for matching docs
        # TODO: Search for matches over corpus titles
        for doc in docs:
            for word in doc:
                if q in word:
                    results.append(doc)
                    break
        
    return render_template("search_results.html", results=results)

if __name__ == '__main__':
    app.run(debug=True)
