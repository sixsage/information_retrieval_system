from search import *
from invertedindex import *

TOTAL_PAGES = 55393

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    #total pages need to be stored 

    if not (os.path.exists("inverted_index.json") and os.path.exists("urlindex.json")):
        total_pages = buildindex()
    user_input = input("SEARCH: ")
    user_input = user_input.split()
    stemmer = PorterStemmer()
    user_input = [stemmer.stem(token) for token in user_input]
    iid = load_json("inverted_index.json")
    urls = load_json("urlindex.json")
    target_doc_ids = query(user_input, iid, TOTAL_PAGES)
    for doc_id in target_doc_ids:
        #print(doc_id)
        print(urls[str(doc_id)])
    print("Top 5 urls: ")
    for doc_id in target_doc_ids[:5]:
        print(urls[str(doc_id)])
