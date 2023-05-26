# Names: Jacob Lee Kyuho Oh Aali Bin Rehan

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
import bisect
import os
import math
import sys

PATH_TO_PAGES = 'DEV'

class InvertedIndexToken:
    def __init__(self, token: str, doc_id: list):
        self.token = token
        self.doc_id = doc_id
    
    def add_docId(self, new_id):
        # this isnt even correct
        # for i,doc in enumerate(self.docId):
        #     if doc < newId:
        #         continue
        # self.docId = self.docId[:i-1] + [newId]  + self.docId[i:]
        bisect.insort(self.doc_id, new_id)
    
class Converter:
    def __init__(self, itt: InvertedIndexToken = None, file: str = None):
        self.itt = itt
        self.file = file
    
    def to_str(self):
        return str(self.itt.token) + ": " + str(self.itt.doc_id)
    
    def to_itt(self):
        file_list = self.file.split(": ")
        token = file_list[0]
        doc_list = list(file_list[1])
        return InvertedIndexToken(token, doc_list)

def tokenizer(content: str):
    tokens = word_tokenize(content)
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(token) for token in tokens]
    return Counter(stemmed_words)

def buildindex():
    #directory = input()
    iid = defaultdict(list)
    # enumerate vs hash ???
    # either way we need to store the mapping
    urls = {}
    page_index = 0
    partial_indexes = []
    for domain in os.scandir(PATH_TO_PAGES):
        for page in os.scandir(domain.path):
            page_index += 1 # enumerate vs hash ???
            with open(page.path, "r") as file:
                data = json.loads(file.read())
                urls[page_index] = data["url"]
                html_content = data["content"]
                text = BeautifulSoup(html_content, "lxml").get_text()
                stems = tokenizer(text)
                for stem in stems:
                    iid[stem].append((page_index, stems[stem]))

                # check accumulated index size with sys.getsizeof(index)
                # if it is over some threshold, dump it into a text file
                # maybe we can add try/except in the case of memory overflow - MemoryError in python 
            print(page_index)
            if page_index % 500 == 0: 
                dump_as_text(f"inverted_index{page_index//500}.txt", iid)
                partial_indexes.append(f"inverted_index{page_index//500}.txt")
                iid = defaultdict(list)
            if page_index >= 2000:
                break
    dump_as_text(f"inverted_index{page_index//500 + 1}.txt", iid)
    partial_indexes.append(f"inverted_index{page_index//500 +1}.txt")


    merge_files("final_index.txt", partial_indexes)
    # after indexing all the pages, we have to merge the created text files
    # open all the files, and read them line by line
    # at the top, get the token that comes first
    # check the line we are currently at for all files to see if there are any other files with that token at the top
    # merge the posting, and put it into the final file
    # note where the posting info will start in the file for the index of the index
    # move the line down afterward


# 1302, 2052
    print(page_index)
    print(len(iid))
    dumping_json = json.dumps(iid)
    dumping_urls = json.dumps(urls)
    with open("inverted_index.json", "w") as opened:
        opened.write(dumping_json)
    with open("urlindex.json", "w") as url_index:
        url_index.write(dumping_urls)

    
def dict_to_str(iid: dict[int, list[(int, int)]]):
    res = ""
    for k in sorted(iid):
        v = ",".join([str(i) for i in iid[k]])
        res += str(k) + "#$%^& " + v + "\n"
    return res.rstrip('\n')

def str_to_dict(line: str):
    parsed = line.split("#$%^& ")
    posting = []
    s = parsed[1]
    for i in range(len(parsed[1])):
        if s[i] == "(":
            res = ""
            i += 1
            while s[i] != ")":
                res += s[i]
                i += 1          
            tup = res.split(",")
            posting.append(tuple([int(tup[0]), float(tup[1])]))
    return {parsed[0]: posting}

def dump_as_text(file: str, iid: dict[int, list[(int,int)]]) -> None:
    with open(file, 'w') as f:
        f.write(dict_to_str(iid))

def merge_postings(allpostings):
    res = []
    for posting in allpostings:
        res.extend(posting)
    return res

def merge_files(output, args):
    file_obj = [open(file) for file in args]
    cur_dicts = [str_to_dict(file.readline()) for file in file_obj]
    out = open(output, 'w')
    while len(cur_dicts) != 0:
        cur_min = list(min([dict.keys() for dict in cur_dicts]))[0]
        cur_postings = []
        for i in range(len(cur_dicts)):
            if i >= len(cur_dicts):
                continue
            if cur_min in cur_dicts[i]:
                cur_postings.append(cur_dicts[i][cur_min])
                line = file_obj[i].readline()
                if line:
                    cur_dicts[i] = str_to_dict(line)
                else:
                    cur_dicts.pop(i)
                    file_obj[i].close()
                    file_obj.pop(i)
        combined = merge_postings(cur_postings)
        final_post = {}
        final_post[cur_min] = combined
        posting = dict_to_str(final_post)
        out.write(posting)
    out.close()

def build_index_of_index(inverted_index):
    token_loc = {}
    with open(inverted_index) as f:
        line = f.readline()
        while line: 
            info = line.split(":")
            token_loc[info[0]] = f.tell() - len(line)
            line = f.readline()
    return token_loc

def find_token(token, token_loc, inverted_index):
    line = ''
    with open(inverted_index) as f:
        f.seek(token_loc[token])
        line = f.readline()
        
    return line
            

if __name__ == "__main__":
    buildindex()
    