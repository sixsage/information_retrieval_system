from collections import defaultdict, Counter
import math
import bisect
import numpy, numpy.linalg
import multiprocessing
import nltk
import time

STOP_WORDS = {'stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'I', 'that', 'had', 'on', 'for', 'were', 'was'}
def tf_idf(term: str, doc_id: int, iid: defaultdict[str, list[(int, int)]], total_pages: int, term_frequency=None):
    if term not in iid:
        return 0
    postings = iid[term]
    if not term_frequency:
        position = bisect.bisect_left(postings, [doc_id])
        term_frequency = -1
        if postings[position][0] == doc_id:
            term_frequency = postings[position][1]
    
    doc_count = len(postings)

    return (1+ math.log(term_frequency)) * math.log(total_pages/doc_count) if term_frequency > 0 else 0


def get_intersection(intersection: list[(int, int)], new_term_postings) -> list[(int, int)]:
    '''
    index 0 should be the docid, index 1 should be the term frequency in the doc
    returns a list of postings - (docid, frequency of the new term inside doc)
    '''
    i = 0
    j = 0
    result = []
    while i < len(intersection) and j < len(new_term_postings):
        if intersection[i][0] == new_term_postings[j][0]:
            result.append(new_term_postings[j])
            i += 1
            j += 1
        elif intersection[i][0] < new_term_postings[j][0]:
            i += 1
        else:
            j += 1
    
    return result

def cosine_similarity(list1: list[int], list2: list[int]):
    return numpy.dot(list1, list2) / (numpy.linalg.norm(list1) * numpy.linalg.norm(list2))

# def single_word_process(q, terms, iid, champion_iid, headings_iid, tagged_iid, total_pages):
def single_word_process(terms, iid, local_iid, headings, tagged, total_pages):
    # assume i am getting the postings as input
    # all of them are dictionaries
    MIN_DOCS = 40
    start_time = time.time()
    unsorted_terms = terms
    terms = sorted(terms, key=lambda x: len(local_iid[x]) if x in local_iid else math.inf)
    doc_scores = dict()
    multiplier = dict()
    visited = set()
    champion_iid = {}
    tagged_iid = {}
    headings_iid = {}
    stop_limit = 0
    # for term in tagged_iid:
    #     for posting in tagged_iid[term]:
    #         doc_id = posting[0]
    #         multiplier[doc_id] = 1.1
    # for term in headings_iid:
    #     for posting in headings_iid[term]:
    #         doc_id = posting[0]
    #         multiplier[doc_id] = 1.3
    for i in range(len(terms)):
        add_more = len(doc_scores) < MIN_DOCS
        if terms[i] in visited:
            continue
        champion_iid.update(iid.find_token_champion(terms[i]))
        headings_iid.update(headings.find_token(terms[i]))
        tagged_iid.update(tagged.find_token(terms[i]))
        visited.add(terms[i])
        for posting in champion_iid[terms[i]]:
            doc_id = posting[0]
            freq = posting[1]
            if doc_id not in doc_scores and add_more:
                doc_scores[doc_id] = [0 for _ in range(len(terms))]
            if doc_id in doc_scores:
                doc_scores[doc_id][i] = (1 + math.log(freq))
        if terms[i] in STOP_WORDS:
            stop_limit += 1
            if stop_limit == 2:
                break
    for term in champion_iid:
        if term in tagged_iid:
            for posting in tagged_iid[term]:
                doc_id = posting[0]
                multiplier[doc_id] = 1.1
        if term in headings_iid:
            for posting in headings_iid[term]:
                doc_id = posting[0]
                multiplier[doc_id] = 1.3
    print('time after getting tf at position', time.time() - start_time)
    query_as_doc = Counter(terms)
    query_score = []
    for term in terms:
        query_score.append(tf_idf(term, -1, local_iid, total_pages, term_frequency=query_as_doc[term]))
    final_score_dict = dict()
    for doc_id in doc_scores:
        final_score_dict[doc_id] = cosine_similarity(doc_scores[doc_id], query_score) * (multiplier[doc_id] if doc_id in multiplier else 1)
    print('time after getting score:', time.time() - start_time)

    # q.put(positional_processing(unsorted_terms, final_score_dict, iid))
    return positional_processing(unsorted_terms, final_score_dict, local_iid)
    return final_score_dict


def query_processing(query, iid, local_iid, bigram_iid, trigram_iid, headings_iid, tagged_iid, total_pages) -> list[int]:
    start_time = time.time()
    # single_queue = multiprocessing.Queue()
    # bigrams_queue = multiprocessing.Queue()
    # trigrams_queue = multiprocessing.Queue()
    # single = multiprocessing.Process(target=single_word_process, args=(single_queue, query, iid, champion_iid, headings_iid, tagged_iid, total_pages))
    # bigrams = multiprocessing.Process(target=ngrams_processing, args=(bigrams_queue, list(nltk.bigrams(query)), bigram_iid))
    # trigrams = multiprocessing.Process(target=ngrams_processing, args=(trigrams_queue, list(nltk.trigrams(query)), trigram_iid))
    # print(' starting the functions', time.time() - start_time)
    # single.start()
    # bigrams.start()
    # trigrams.start()
    # print('after starting the functions', time.time() - start_time)
    # candidates = single_queue.get()
    # bigram_scores = bigrams_queue.get()
    # trigram_scores = trigrams_queue.get()
    candidates = single_word_process(query, iid, local_iid, headings_iid, tagged_iid, total_pages)
    bigram_multiplied = ngrams_processing(list(nltk.bigrams(query)), candidates, bigram_iid)
    trigram_multiplied = ngrams_processing(list(nltk.trigrams(query)), bigram_multiplied, trigram_iid)
    print('after all functions runs', time.time() - start_time)
    # single.join()
    # bigrams.join()
    # trigrams.join()
    result = [docid for docid in sorted(trigram_multiplied, key=lambda x: trigram_multiplied[x], reverse=True)]
    print('after everything and sorting', time.time() - start_time)
    return result





# def ngrams_processing(q: multiprocessing.Queue, terms, special_iid) -> dict[int, int]:
def ngrams_processing(terms, candidates, special) -> dict[int, int]:
    start_time = time.time()
    doc_scores = defaultdict(int)
    special_iid = {}
    visited = set()
    for term in terms:
        if term in visited:
            continue
        special_iid.update(special.find_token(term))
        visited.add(term)
        if term not in special_iid:
            continue
        docs = [(x[0], x[1]) for x in special_iid[term] if x[0] in candidates]
        for doc in docs:
            doc_scores[doc[0]] += doc[1]
    for doc_id in doc_scores:
        doc_scores[doc_id] = doc_scores[doc_id] * .02 + 1
        
    # q.put(doc_scores)
    for doc_id in candidates:
        candidates[doc_id] *= doc_scores[doc_id]
    print('ngrams takes:', time.time() - start_time)
    return candidates

def positional_processing(query, cand_docids: dict, local_iid):
    start_time = time.time()
    terms: list[(str, str, int)] = posify(query)
    for term in terms:
        if term[0] not in local_iid or term[1] not in local_iid:
            continue
        first_posting = local_iid[term[0]]
        second_posting = local_iid[term[1]]
        i = 0
        j = 0
        while i < len(first_posting) and j < len(second_posting):
            if first_posting[i][0] == second_posting[j][0] and first_posting[i][0] in cand_docids:
                freq = positional_matching(first_posting[i], second_posting[j], term[2])
                cand_docids[first_posting[i][0]] *= freq * .2 + 1
                i += 1
                j += 1
            elif first_posting[i][0] < second_posting[j][0]:
                i += 1
            else:
                j += 1
    print('positional processing takes:', time.time() - start_time)
    return cand_docids
        
def posify(query):
    if len(query) <= 3:
        return []
    res = []
    i = 0
    while i < len(query):
        j = i + 3
        while j < len(query):
            if query[i] in STOP_WORDS:
                break
            elif query[j] not in STOP_WORDS:
                res.append((query[i],query[j],j-i))
                if len(res) == 5:
                    return res
            j += 1
        i += 1
    return res



def positional_matching(list1: list[int], list2: list[int], target) -> set[int]:
    'Find how many integers in the list1 are a target number difference from list2'
    i = 2
    j = 2
    res = 0
    # print(list1, list2)
    while i < len(list2) and j < len(list1):
        if list2[i] - list1[j] == target:
            i += 1
            j += 1
            res += 1
        elif list2[i] - list1[j] < target:
            i += 1
        else:
            j += 1    
    return res
