import search
import invertedindex
from nltk.stem import PorterStemmer
import os
import json

TOTAL_PAGES = 55393

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    #total pages need to be stored 

    # if not (os.path.exists("final_index.txt") and os.path.exists("urlindex.json")):
    #     total_pages = invertedindex.buildindex()
    iid = invertedindex.InvertedIndex()
    #iid = load_json("inverted_index.json")
    ioi = invertedindex.build_index_of_index(iid)
    urls = load_json(iid.urlindex)
    user_input = input("SEARCH: ")
    user_input = user_input.split()
    stemmer = PorterStemmer()
    user_input = [stemmer.stem(token) for token in user_input]
    query_iid = {}
    for token in user_input:
        query_iid.update(iid.str_to_dict(invertedindex.find_token(token, ioi, iid)))
    
    target_doc_ids = search.query_processing(user_input, query_iid, TOTAL_PAGES)
    # for doc_id in target_doc_ids:
    #     #print(doc_id)
    #     print(urls[str(doc_id)])
    print("Top 5 urls: ")
    for doc_id in target_doc_ids[:5]:
        print(urls[str(doc_id)])
