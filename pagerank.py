# just all strings?
import json

class PageRank:
    
    def __init__(self):
        self.directs_to = dict() # dict[docid] = list of all docids that this doc points to
        self.directed_by  = dict() # dict[docid] = list of all docids that points to this doc
        self.link_to_docid = dict()
        with open("urlindex.json", "r") as f:
            x = f.read()
            link_mapping = json.loads(x)
            for k, v in link_mapping.items():
                self.link_to_docid[v] = k

    def add_link(self, doc, links_in_doc):
        '''
        doc = docid
        links_in_doc = links that are in the doc
        '''
        



    def calculate_pagerank(self):
        pass