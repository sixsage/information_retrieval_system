from collections import defaultdict
import math
import bisect

def tf_idf(term: str, doc_id: int, iid: defaultdict[list, int], total_pages: int):
    posting = iid[term]
    freq = -1
    # for page in posting:
    #     if page[0] == docID:
    #         freq = page[1]
    #         break
    position = bisect.bisect_left(posting, [doc_id])
    if posting[position][0] == doc_id:
        freq = posting[position][1]
    
    doc_count = len(posting)

    return (1+ math.log(freq)) * math.log(total_pages/doc_count) if freq > 0 else 0



def query(terms: list[str], iid: dict[str, list[int]], total_pages) -> list[int]:
    terms = sorted(terms, key=lambda x: len(iid[x]))
    docs = None
    ranks = {}
    for term in terms:
        if docs == None:
            docs = iid[term]
        else:
            new_docs = iid[term]
            i = 0 # index for old docs
            u = 0 # index for new term docs
            new = [] # resulting intersection of docs
            while i < len(docs) and u < len(new_docs):
                if docs[i][0] == new_docs[u][0]:
                    rank = tf_idf(term, docs[i][0], iid, total_pages)
                    ranks[str(docs[i][0])] = rank
                    new.append(docs[i])
                    i += 1
                    u += 1
                elif docs[i][0] < new_docs[u][0]:
                    i += 1
                else:
                    u += 1
            docs = new

        
    ordered = sorted(docs, key= lambda x: ranks[str(x[0])], reverse=True)
    return [x[0] for x in ordered]