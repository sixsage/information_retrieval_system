
def query(terms: list[str], iid: dict[str, list[int]]) -> list[int]:
    terms = sorted(terms, key=lambda x: len(iid[x]))
    docs = None
    for term in terms:
        if docs == None:
            docs = iid[term]
        else:
            newdocs = iid[term]
            i = 0 # index for old docs
            u = 0 # index for new term docs
            new = [] # resulting intersection of docs
            while i < len(docs) and u < len(newdocs):
                if docs[i][0] == newdocs[u][0]:
                    new.append(docs[i])
                    i += 1
                    u += 1
                elif docs[i][0] < newdocs[u][0]:
                    i += 1
                else:
                    u += 1
            docs = new
    return [x[0] for x in docs]