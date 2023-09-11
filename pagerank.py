# just all strings?
import json
from urllib.parse import urlparse, urldefrag, urljoin
from collections import defaultdict

class PageRank:
    
    def __init__(self):
        self.directs_to = defaultdict(list) # dict[docid] = list of all docids that this doc points to
        self.directed_by  = defaultdict(list) # dict[docid] = list of all docids that points to this doc
        self.link_to_docid = dict()
        with open("urlindex.json", "r") as f:
            x = f.read()
            self.link_mapping = json.loads(x)
            for k, v in self.link_mapping.items():
                self.link_to_docid[v] = int(k)

    def _get_absolute_path(self, path: str, current_url: str) -> str:
        path = urldefrag(path)[0]
        return urljoin(current_url, path)

    def add_link(self, doc, links_in_doc):
        '''
        doc = docid
        links_in_doc = list of links that are in the doc
        '''
        original_url = self.link_mapping[str(doc)]
        links_in_doc = [self._get_absolute_path(original_url, link) for link in links_in_doc]
        for link in links_in_doc:
            if link in self.link_to_docid:
                link_docid = self.link_to_docid[link]
                self.directs_to[doc].append(link_docid)
                self.directed_by[link_docid].append(doc)

    def _calculate_pagerank(self, docid, damping_factor):
        result = 0
        for link in self.directed_by[docid]:
            result += self.pageranks[link] / len(self.directs_to[link])
        return 1 - damping_factor + 0.85 * result

    def get_pageranks(self, damping_factor = 0.85, iterations = 10):
        # assign the pagerank records as attribute?
        self.pageranks = [1] * (len(self.link_to_docid) + 1) # to account for 1-indexed docids

        for _ in range(iterations):
            new_iteration = [0] * len(self.pageranks)
            for docid in range(1, len(self.pageranks)):
                new_iteration[docid] = self._calculate_pagerank(docid, damping_factor)
            self.pageranks = new_iteration

        with open('pagerank.json', 'w') as f:
            json.dump(self.pageranks, f)