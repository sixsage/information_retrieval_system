import search
import invertedindex
from nltk.stem import PorterStemmer
import os
import json
import multiprocessing

TOTAL_PAGES = 55393

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    #total pages need to be stored 

    if not (os.path.exists("final_index1.txt") and os.path.exists("urlindex.json")):
        total_pages = invertedindex.build_indexes()
    iid = invertedindex.InvertedIndex()
    iid.build_index_of_index()
    bigrams = invertedindex.BigramIndex()
    bigrams.build_index_of_index()
    trigrams = invertedindex.TrigramIndex()
    trigrams.build_index_of_index()
    #iid = load_json("inverted_index.json")
    urls = load_json("urlindex.json")
    stemmer = PorterStemmer()
    user_input = input("SEARCH: ")
    user_input = user_input.split()
    user_input = [stemmer.stem(token) for token in user_input]
    query_iid = {}
    for token in user_input:
        query_iid.update(iid.find_token(token))
    # print(query_iid)

    # MULTIPROCESSING IN PROGRESS
    # make the query_iid in query_processing? passing in the index objects for now
    # processbigrams = multiprocessing.Process(target=search.query_processing, args=[search.bigramify_query(user_input), bigrams, TOTAL_PAGES])

    # processtrigrams = multiprocessing.Process(target=search.query_processing, args=[search.trigramify_query(user_input), trigrams, TOTAL_PAGES])

    # processpositional = multiprocessing.Process(target=search.query_processing, args=[search.trigramify_query(user_input), trigrams, TOTAL_PAGES])

    target_doc_ids = search.query_processing(user_input, query_iid, TOTAL_PAGES)


    # for doc_id in target_doc_ids:
    #     #print(doc_id)
    #     print(urls[str(doc_id)])
    print("Top 10 urls: ")
    for doc_id in target_doc_ids[:10]:
        print(urls[str(doc_id)])
