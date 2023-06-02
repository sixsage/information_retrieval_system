import search
import invertedindex
from nltk.stem import PorterStemmer
import os
import json
import multiprocessing
import datetime

TOTAL_PAGES = 41522

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    #total pages need to be stored 

    if not (os.path.exists("final_index1.txt") and os.path.exists("urlindex.json")):
        invertedindex.build_indexes()
    headings_iid = invertedindex.InvertedIndex("final_headings_index", "headings_index")
    headings_iid.build_index_of_index()
    iid = invertedindex.InvertedIndex()
    iid.build_index_of_index()
    tagged_iid = invertedindex.InvertedIndex("final_tagged_index.txt", "tagged_index")
    tagged_iid.build_index_of_index()
    bigrams = invertedindex.BigramIndex()
    bigrams.build_index_of_index()
    trigrams = invertedindex.TrigramIndex()
    trigrams.build_index_of_index()
    #iid = load_json("inverted_index.json")
    urls = load_json("urlindex.json")
    stemmer = PorterStemmer()
    user_input = input("SEARCH: ")
    strat_time = datetime.datetime.now()
    user_input = user_input.split()
    terms = [stemmer.stem(token) for token in user_input]
    local_iid = {}
    bigram_iid = {}
    trigram_iid = {}
    for token in terms:
        local_iid.update(iid.find_token(token))
        bigram_iid.update(bigrams.find_token(token))
        trigram_iid.update(trigrams.find_token(token))
    
    # print(query_iid) 
    result = search.query_processing(terms, iid, bigram_iid, trigram_iid, headings_iid, tagged_iid, TOTAL_PAGES)

    
    print("Top 10 urls: ")
    for doc_id in result[:10]:
        print(urls[str(doc_id)])
    end_time = datetime.datetime.now()
    duration = (strat_time - end_time).microseconds /1000
    # for doc_id in target_doc_ids:
    #     #print(doc_id)
    #     print(urls[str(doc_id)])
