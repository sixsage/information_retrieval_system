import search
import invertedindex
from nltk.stem import PorterStemmer
import os
import json
import multiprocessing
import datetime
import nltk

TOTAL_PAGES = 41522

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)

if __name__ == "__main__":
    #total pages need to be stored 

    if not (os.path.exists("final_index1.txt") and os.path.exists("urlindex.json")):
        invertedindex.build_indexes()
    headings_iid = invertedindex.InvertedIndex("final_headings_index.txt", "headings_index")
    if os.path.exists("headings_ioi.json"):
        load_json("headings_ioi.json")
    else:
        headings_iid.build_index_of_index()
        dumping_ioi = json.dumps(headings_iid.token_loc)
        with open("headings_ioi.json", "w") as f:
            f.write(dumping_ioi)
    iid = invertedindex.InvertedIndex()
    if os.path.exists("iid_ioi.json"):
        load_json("iid_ioi.json")
    else:
        iid.build_index_of_index()
        dumping_ioi = json.dumps(iid.token_loc)
        with open("iid_ioi.json", "w") as f:
            f.write(dumping_ioi)
    tagged_iid = invertedindex.InvertedIndex("final_tagged_index.txt", "tagged_index")
    if os.path.exists("tagged_ioi.json"):
        load_json("tagged_ioi.json")
    else:
        tagged_iid.build_index_of_index()
        dumping_ioi = json.dumps(tagged_iid.token_loc)
        with open("tagged_ioi.json", "w") as f:
            f.write(dumping_ioi)
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
    for token in nltk.bigrams(terms):
        bigram_iid.update(bigrams.find_token(token))
    for toke in nltk.trigrams(terms):
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
