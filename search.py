from collections import defaultdict, Counter
import math
import bisect
import numpy, numpy.linalg

def tf_idf(term: str, doc_id: int, iid: defaultdict[str, list[(int, int)]], total_pages: int, term_frequency=None):
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

def query_processing(q, terms: list[str | tuple], iid: dict[str, list[tuple[int]]], total_pages) -> list[int]:
    query_iid = {}
    for token in terms:
        query_iid.update(iid.find_token(token))
    terms = sorted(terms, key=lambda x: len(query_iid[x]))
    intersection = None
    doc_scores = defaultdict(list)
    for term in terms:
        if intersection == None:
            intersection = [(x[0], x[1]) for x in query_iid[term]]
        else:
            new_term_postings = [(x[0], x[1]) for x in query_iid[term]]
            intersection = get_intersection(intersection, new_term_postings)
        for doc_id, frequency in intersection:
            doc_scores[doc_id].append(1+ math.log(frequency))
    
    # calculate the cosine similarity
    query_as_doc = Counter(terms)
    query_score = []
    for term in terms:
        print(term)
        query_score.append(tf_idf(term, -1, query_iid, total_pages, term_frequency=query_as_doc[term]))
    pages_with_all_terms = [doc_id for doc_id in doc_scores if len(doc_scores[doc_id]) == len(query_score)]
    ranking = sorted(pages_with_all_terms, 
                     key= lambda doc_id: cosine_similarity(doc_scores[doc_id], query_score), reverse=True)
    print(ranking)
    q.put(ranking)

def bigramify_query(terms: list[str]) -> list[str]:
    'Change query to index bigrams index'
    bigrams = []
    prev = terms[0]
    for term in terms[1:]:
        bigrams.append((prev, term))
    return bigrams
        

def trigramify_query(terms: list[str]) -> list[str]:
    'Change query to index trigrams index'
    pass

def positional_matching(list1: list[int], list2: list[int], target) -> set[int]:
    'Find how many integers in the list1 are a target number difference from list2'
    i = 0
    j = 0
    res = 0
    while i < len(list1) and j < len(list2):
        if list2[i] - list1[i] == target:
            i += 1
            j += 1
            res += 1
        elif list2[i] - list1[i] > target:
            i += 1
        else:
            j += 1    
    return res

def positional_processing(terms: list[str], iid: dict[str, list[tuple[int]]]) -> int:
    '''
    Enumerates valid term pairs and determines if there is a positional difference match 
    in the inverted index
    '''
    pass