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
    print(list1, list2)
    return numpy.dot(list1, list2) / (numpy.linalg.norm(list1) * numpy.linalg.norm(list2))

def query_processing(terms: list[str], iid: dict[str, list[(int, int)]], total_pages) -> list[int]:
    terms = sorted(terms, key=lambda x: len(iid[x]))
    intersection = None
    doc_scores = defaultdict(list)
    for term in terms:
        if intersection == None:
            intersection = iid[term]
        else:
            new_term_postings = iid[term]
            intersection = get_intersection(intersection, new_term_postings)
        for doc_id, frequency in intersection:
            doc_scores[doc_id].append(1+ math.log(frequency))
    
    # for tf idf sum ranking
    # for term in terms:
    #     for doc_id, _ in intersection:
    #         doc_scores[doc_id].append(tf_idf(term, doc_id, iid, total_pages))

    # for cosine similarity
    # for term in terms:
    #     for doc_id, frequency in intersection:
    #         doc_scores[doc_id].append(1+ math.log(frequency))
    # calculate the cosine similarity
    query_as_doc = Counter(terms)
    query_score = []
    for term in terms:
        query_score.append(tf_idf(term, -1, iid, total_pages, term_frequency=query_as_doc[term]))
    pages_with_all_terms = [doc_id for doc_id in doc_scores if len(doc_scores[doc_id]) == len(query_score)]
    ranking = sorted(pages_with_all_terms, 
                     key= lambda doc_id: cosine_similarity(doc_scores[doc_id], query_score), reverse=True)
    return ranking

    # for tf_idf sum ranking
    # ranking = sorted(doc_scores.keys(), key=lambda doc_id: sum(doc_scores[doc_id]), reverse=True)
    # return ranking

    # for term in terms:
    #     if docs == None:
    #         docs = iid[term]
    #     new_docs = iid[term]
    #     i = 0 # index for old docs
    #     u = 0 # index for new term docs
    #     new = [] # resulting intersection of docs
    #     while i < len(docs) and u < len(new_docs):
    #         if docs[i][0] == new_docs[u][0]:
    #             if str(docs[i][0]) not in ranks:
    #                 rank = tf_idf(term, docs[i][0], iid, total_pages)
    #                 ranks[str(docs[i][0])] = rank
    #             new.append(docs[i])
    #             i += 1
    #             u += 1
    #         elif docs[i][0] < new_docs[u][0]:
    #             i += 1
    #         else:
    #             u += 1
    #     docs = new
        
    # ordered = sorted(docs, key= lambda x: ranks[str(x[0])], reverse=True)
    # return [x[0] for x in ordered]