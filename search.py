from collections import defaultdict, Counter
import math
import bisect
import numpy, numpy.linalg
import multiprocessing
import nltk
import time
TOTAL_PAGES = 0

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

def single_word_process(q, terms, iid, headings_iid, tagged_iid, total_pages):
    # assume i am getting the postings as input
    # all of them are dictionaries
    MIN_DOCS = 30

    terms.sort(key=lambda x: len(iid[x]) if x in iid else math.inf)
    doc_scores = dict()
    multiplier = dict()
    for term in tagged_iid:
        for posting in tagged_iid[term]:
            doc_id = posting[0]
            multiplier[doc_id] = 1.1
    for term in headings_iid:
        for posting in headings_iid[term]:
            doc_id = posting[0]
            multiplier[doc_id] = 1.3

    for i in range(len(terms)):
        add_more = len(doc_scores) < MIN_DOCS
        if terms[i] not in iid:
            continue
        for posting in iid[terms[i]]:
            doc_id = posting[0]
            freq = posting[1]
            if doc_id not in doc_scores and add_more:
                doc_scores[doc_id] = [0 for _ in range(len(terms))]
            if doc_id in doc_scores:
                doc_scores[doc_id][i] = (1 + math.log(freq))

    query_as_doc = Counter(terms)
    query_score = []
    for term in terms:
        query_score.append(tf_idf(term, -1, iid, total_pages, term_frequency=query_as_doc[term]))
    final_score_dict = dict()
    for doc_id in doc_scores:
        final_score_dict[doc_id] = cosine_similarity(doc_scores[doc_id], query_score) * (multiplier[doc_id] if doc_id in multiplier else 1)

    q.put(positional_processing(terms, final_score_dict, iid))


def query_processing(query, iid, bigram_iid, trigram_iid, headings_iid, tagged_iid, total_pages) -> list[int]:
    single_queue = multiprocessing.Queue()
    bigrams_queue = multiprocessing.Queue()
    trigrams_queue = multiprocessing.Queue()
    single = multiprocessing.Process(target=single_word_process, args=(single_queue, query, iid, headings_iid, tagged_iid, total_pages))
    bigrams = multiprocessing.Process(target=ngrams_processing, args=(bigrams_queue, list(nltk.bigrams(query)), bigram_iid))
    trigrams = multiprocessing.Process(target=ngrams_processing, args=(trigrams_queue, list(nltk.trigrams(query)), trigram_iid))
    # start = time.time_ns()
    # single.start()
    # candidates = single_queue.get()
    # time_sec = time.time_ns()
    # print("single",(time_sec-start)/1000000)
    # start = time.time_ns()
    # bigrams.start()
    # bigram_scores = bigrams_queue.get()
    # time_sec = time.time_ns()
    # print("bi",(time_sec-start)/1000000)
    # start = time.time_ns()
    # trigrams.start()
    # trigram_scores = trigrams_queue.get()
    # time_sec = time.time_ns()
    # print("tri",(time_sec-start)/1000000)
    single.start()
    bigrams.start()
    trigrams.start()
    candidates = single_queue.get()
    bigram_scores = bigrams_queue.get()
    trigram_scores = trigrams_queue.get()
    for k in candidates:
        candidates[k] *= bigram_scores[k] if k in bigram_scores else 1
        candidates[k] *= trigram_scores[k] if k in trigram_scores else 1
    single.join()
    bigrams.join()
    trigrams.join()
    return [docid for docid in sorted(candidates, key=lambda x: candidates[x], reverse=True)]





def ngrams_processing(q: multiprocessing.Queue, terms, special_iid) -> dict[int, int]:
    terms = sorted(terms, key=lambda x: len(special_iid[x]) if x in special_iid else math.inf)
    doc_scores = {}
    intersection = None
    for term in terms:
        if term not in special_iid:
            continue
        if intersection == None:
            intersection = [(x[0], x[1]) for x in special_iid[term]]
        else:
            new_term_postings = [(x[0], x[1]) for x in special_iid[term]]
            intersection = get_intersection(intersection, new_term_postings)
    if intersection:
        for doc_id, frequency in intersection:
            doc_scores[doc_id] = frequency * .05 + 1
    q.put(doc_scores)

def positional_processing(query, cand_docids: dict, local_iid):
    terms: list[(str, str, int)] = posify(query)
    for term in terms:
        if term[0] not in local_iid or term[1] not in local_iid:
            continue
        first_posting = local_iid[term[0]]
        second_posting = local_iid[term[1]]
        i = 0
        j = 0
        while i < len(first_posting) and j < len(second_posting):
            if first_posting[i][0] == second_posting[i][0] and first_posting[i][0] in cand_docids:
                freq = positional_matching(first_posting[i], second_posting[i], term[2])
                cand_docids[first_posting[i][0]] *= freq * .05 + 1
                i += 1
                j += 1
            elif first_posting[i][0] < second_posting[i][0]:
                i += 1
            else:
                j += 1
    return cand_docids
        
def posify(query):
    stopwords = set()
    if len(query) <= 3:
        return []
    res = []
    i = 0
    while i < len(query):
        j = i + 3
        while j < len(query):
            if query[i] in stopwords:
                break
            elif query[j] not in stopwords:
                res.append((query[i],query[j],j-i))
            j += 1
        i += 1
    return res



def positional_matching(list1: list[int], list2: list[int], target) -> set[int]:
    'Find how many integers in the list1 are a target number difference from list2'
    i = 2
    j = 2
    res = 0
    print(list1, list2)
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
