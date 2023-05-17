from search import *
from invertedindex import *

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    user_input = input("SEARCH: ")
    user_input = user_input.split()
    stemmer = PorterStemmer()
    user_input = [stemmer.stem(token) for token in user_input]
    iid = load_json("inverted_index.json")
    #urls = load_json("urlindex.json")
    targetDocIds = query(user_input, iid)
    for docid in targetDocIds:
        print(docid)
        #print(urls[docid])

