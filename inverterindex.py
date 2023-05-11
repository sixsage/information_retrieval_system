from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
from hashlib import sha256
import lxml
import bisect
import os

PATH_TO_PAGES = 'DEV'

class InvertedIndexToken:
    def __init__(self, token: str, docId: list):
        self.token = token
        self.docId = docId
    
    def add_docId(self, newId):
        # this isnt even correct
        # for i,doc in enumerate(self.docId):
        #     if doc < newId:
        #         continue
        # self.docId = self.docId[:i-1] + [newId]  + self.docId[i:]
        bisect.insort(self.docId, newId)
    
class Converter:
    def __init__(self, itt: InvertedIndexToken = None, filestr: str = None):
        self.itt = itt
        self.filestr = filestr
    
    def to_str(self):
        return str(self.itt.token) + ": " + str(self.itt.docId)
    
    def to_itt(self):
        splitstr = self.filestr.split(": ")
        token = splitstr[0]
        doclist = list(splitstr[1])
        return InvertedIndexToken(token, doclist)

def tokenizer(content: str):
    tokens = word_tokenize(content)
    stemmer = PorterStemmer()
    stemed_words = [stemmer.stem(token) for token in tokens]
    return Counter(stemed_words)

if __name__ == "__main__":
    #directory = input()
    iid = defaultdict(list)
    # enumerate vs hash ???
    # either way we need to store the mapping
    pageIndex = 0
    for domain in os.scandir(PATH_TO_PAGES):
        for page in os.scandir(domain.path):
            pageIndex += 1 # enumerate vs hash ???
            with open(page.path, "r") as file:
                data = json.loads(file.read())
                html_content = data["content"]
                text = BeautifulSoup(html_content, "lxml").get_text()
                stems = tokenizer(text)
                for stem in stems:
                    iid[stem].append((pageIndex, stems[stem]))
    dumpingJson = json.dumps(iid)
    with open("inverted_index.json", "w") as opened:
        opened.write(dumpingJson)
                