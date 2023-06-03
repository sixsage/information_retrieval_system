import search
import invertedindex
from nltk.stem import PorterStemmer
import os
import json
import multiprocessing
import datetime, time
import nltk
import time
import streamlit as st
import pandas as pd 

TOTAL_PAGES = 41522
STOP_WORDS = {'stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'I', 'that', 'had', 'on', 'for', 'were', 'was', 'how', 'of', 'do'}

def load_json(file):
    with open(file, "r") as f:
        x = f.read()
        return json.loads(x)
    
def get_results(user_query):
        print("user query:", user_query)
        s_time = time.time()
        st.session_state["user_query"] = user_query
        user_input = user_query

        user_input = user_input.split()
        terms = [stemmer.stem(token) for token in user_input]
        for token in terms:
            if token not in local_iid:
                local_iid.update(iid.find_token(token))

        result = search.query_processing(terms, iid, local_iid, bigrams, trigrams, headings, tagged, TOTAL_PAGES)
        print("got results", result[:10])
        e_time = time.time()

        #links = []
        #print("Top 10 urls: ")
        duration_time = (e_time - s_time) * 1000
        st.write("results for ", user_query, ":", "computed in: ", duration_time, "ms")
        for doc_id in result[:10]:
            print(urls[str(doc_id)])
            st.write(f'[{urls[str(doc_id)]}](%s)' % urls[str(doc_id)])
            #links.append(str(doc_id))
    
        print(duration_time)
        #links = getLinks(300)
        #time = len(links)

        #return links[:10]
        
def get_query(q):
    st.write(q)
    print(q)
    return
def update():
    s_time = time.time()
    print("inupdate", st.session_state.user_query)
    user_input = st.session_state.user_query

    user_input = user_input.split()
    terms = [st.session_state["stemmer"].stem(token) for token in user_input]
    for token in terms:
        if token not in st.session_state["local_iid"]:
            st.session_state["local_iid"].update(st.session_state["iid"].find_token(token))

    result = search.query_processing(terms, st.session_state["iid"], st.session_state["local_iid"], st.session_state["bigrams"], st.session_state["trigrams"], st.session_state["headings"], st.session_state["tagged"], TOTAL_PAGES)
    print("got results", result[:10])
    e_time = time.time()

    #links = []
    #print("Top 10 urls: ")
    st.session_state["results"] = result
    duration_time = (e_time - s_time) * 1000
    st.session_state["duration"] = duration_time
    st.session_state["user_query"] = ""
    # st.write("results for ", user_input, ":", "computed in: ", duration_time, "ms")
    # for doc_id in result[:10]:
    #     url = st.session_state["urls"][str(doc_id)]
    #     print(url)
    #     st.write(f'[{url}](%s)' % url)
        #links.append(str(doc_id))

    print(duration_time)



if __name__ == "__main__":
#total pages need to be stored 

    if "start" not in st.session_state:
        st.session_state["start"] = 1

    if st.session_state.start == 1:
        print("indexing", st.session_state.start)
        if not (os.path.exists("final_index1.txt") and os.path.exists("urlindex.json")):
            #invertedindex.build_indexes()
            pass
        headings = invertedindex.InvertedIndex("final_headings_index.txt", "headings_index")
        if os.path.exists("headings_ioi.json"):
            x = load_json("headings_ioi.json")
            headings.token_loc = x
        else:
            headings.build_index_of_index()
            dumping_ioi = json.dumps(headings.token_loc)
            with open("headings_ioi.json", "w") as f:
                f.write(dumping_ioi)
        iid = invertedindex.InvertedIndex()
        if not os.path.exists("champion_index.txt"):
            iid.create_champion_list()
        if os.path.exists("champ_ioi.json"):
            x = load_json("champ_ioi.json")
            iid.token_loc = x
        else:
            iid.build_champion_index_of_index()
            dumping_ioi = json.dumps(iid.champion_loc)
            with open("champ_ioi.json", "w") as f:
                f.write(dumping_ioi)
        iid.build_champion_index_of_index()
        if os.path.exists("iid_ioi.json"):
            x = load_json("iid_ioi.json")
            iid.token_loc = x
        else:
            iid.build_index_of_index()
            dumping_ioi = json.dumps(iid.token_loc)
            with open("iid_ioi.json", "w") as f:
                f.write(dumping_ioi)
        tagged = invertedindex.InvertedIndex("final_tagged_index.txt", "tagged_index")
        if os.path.exists("tagged_ioi.json"):
            x = load_json("tagged_ioi.json")
            tagged.token_loc = x
        else:
            tagged.build_index_of_index()
            dumping_ioi = json.dumps(tagged.token_loc)
            with open("tagged_ioi.json", "w") as f:
                f.write(dumping_ioi)
        bigrams = invertedindex.BigramIndex()
        bigrams.build_index_of_index()
        trigrams = invertedindex.TrigramIndex()
        trigrams.build_index_of_index()
        #iid = load_json("inverted_index.json")
        urls = load_json("urlindex.json")

            
        stemmer = PorterStemmer()
        st.session_state.start += 1
        print(st.session_state.start)

        
        local_iid = {}
        bigram_iid = {}
        trigram_iid = {}
        headings_iid = {}
        tagged_iid = {}
        champion_iid = {}
        if "stemmer" not in st.session_state:
            st.session_state["stemmer"] = stemmer

        if "local_iid" not in st.session_state:
            st.session_state["local_iid"] = local_iid
        if "iid" not in st.session_state:
            st.session_state["iid"] = iid
        if "headings" not in st.session_state:
            st.session_state["headings"] = headings
        if "bigrams" not in st.session_state:
            st.session_state["bigrams"] = bigrams
        if "trigrams" not in st.session_state:
            st.session_state["trigrams"] = trigrams
        if "tagged" not in st.session_state:
            st.session_state["tagged"] = tagged
        if "urls" not in st.session_state:
            st.session_state["urls"] = urls
        
        for token in STOP_WORDS:
            st.session_state["local_iid"].update(st.session_state["iid"].find_token(st.session_state["stemmer"].stem(token)))
    #while True:
        #user_input = input("SEARCH: ")
    st.set_page_config(page_title="search")

    st.title("Home page")
    # if "user_query" not in st.session_state:
    #     st.session_state["user_query"] = ""

    if "user_query" not in st.session_state:
        st.session_state["user_query"] = ""

    q = st.text_input("search",on_change=update, key = "user_query")
    if "results" in st.session_state:
        st.write("results computed in: ", st.session_state["duration"], "ms")
        for doc_id in st.session_state["results"]:
            url = st.session_state["urls"][str(doc_id)]
            print(url)
            st.write(f'[{url}]({url})')
    print("search complete")
    st.write("yay")

    #st.session_state["user_query"] = user_query

    #save = st.button("save")
    #get_data().append({"user_query": user_query})
    #st.session_state["user_query"] = user_query
    #st.write(pd.DataFrame(get_data()))
    print("got iuser query:", q, st.session_state.user_query)
    print('creating buton')
    #submit = st.button("submit" )

    