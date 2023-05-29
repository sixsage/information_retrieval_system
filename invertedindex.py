# Names: Jacob Lee Kyuho Oh Aali Bin Rehan

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
import os


class Index:
    def __init__(self) -> None:
        self.path_to_pages = 'DEV'
        self.partial_indexes = []
        self.index = defaultdict(list)
        self.dump_threshold = 15000
        self.location = ""
        self.splitter = "#$%^& "
        self.urlindex = "urlindex.json"
    
    def tokenizer(self, content: str):
        tokens = word_tokenize(content)
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(token) for token in tokens]
        return Counter(stemmed_words)
    
    def merge_postings(self, allpostings):
        res = []
        for posting in allpostings:
            res.extend(posting)
        return res
    
    def str_to_dict(self, line):
        return dict(line)
    
    def dict_to_str(self, dict):
        return str(dict)
    
    # after indexing all the pages, we have to merge the created text files
    # open all the files, and read them line by line
    # at the top, get the token that comes first
    # check the line we are currently at for all files to see if there are any other files with that token at the top
    # merge the posting, and put it into the final file
    # note where the posting info will start in the file for the index of the index
    # move the line down afterward

    def merge_files(self):
        file_obj = [open(file, encoding="utf-8") for file in self.partial_indexes]
        cur_dicts = [self.str_to_dict(file.readline()) for file in file_obj]
        out = open(self.location, 'w', encoding="utf-8")
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
                        cur_dicts[i] = self.str_to_dict(line)
                    else:
                        cur_dicts.pop(i)
                        file_obj[i].close()
                        file_obj.pop(i)
            combined = self.merge_postings(cur_postings)
            final_post = {}
            final_post[cur_min] = combined
            posting = self.dict_to_str(final_post)
            out.write(posting)
        out.close()
    
    def dump_as_text(self, file: str, iid: dict) -> None:
        with open(file, 'w', encoding="utf-8") as f:
            f.write(self.dict_to_str(iid))
    
    def dump(self, filename: str):
        self.dump_as_text(filename, self.index)
        self.partial_indexes.append(filename)
        self.index = defaultdict(list)

class InvertedIndex(Index):
    def __init__(self) -> None:
        super().__init__()
        self.location = "final_index.txt"
        self.urls = None
        if not os.path.exists(self.urlindex):
            self.urls = {}
        if not os.path.exists(self.location):
            self.build_index()

    def build_index(self) -> None:
        page_index = 0
        for domain in os.scandir(self.path_to_pages):
            for page in os.scandir(domain.path):
                page_index += 1
                with open(page.path, "r") as file:
                    data = json.loads(file.read())
                    if self.urls is not None:
                        self.urls[page_index] = data["url"]
                    html_content = data["content"]
                    text = BeautifulSoup(html_content, "lxml").get_text()
                    stems = self.tokenizer(text)
                    for stem in stems:
                        self.index[stem].append((page_index, stems[stem]))

                    # check accumulated index size with sys.getsizeof(index)
                    # if it is over some threshold, dump it into a text file
                    # maybe we can add try/except in the case of memory overflow - MemoryError in python 
                print(page_index)
                if page_index % self.dump_threshold == 0: 
                    self.dump(f"inverted_index{page_index//self.dump_threshold}.txt")

            # if you want to test with smaller values uncomment below and change self.dump_threshold in base class
            # (should also change self.location in this class so it doesn't mess up your current index)
            #     if page_index > 2000:
            #         break
            # if page_index > 2000:
            #     break
            
        self.dump(f"inverted_index{page_index//self.dump_threshold + 1}.txt")
        self.merge_files()
        
        if self.urls is not None:
            dumping_urls = json.dumps(self.urls)
            with open(self.urlindex, "w") as url_index:
                url_index.write(dumping_urls)
            
    def dict_to_str(self, iid: dict[int, list[(int, int)]]):
        res = ""
        for k in sorted(iid):
            v = ",".join([str(i) for i in iid[k]])
            res += str(k) + self.splitter + v + "\n"
        return res

    def str_to_dict(self, line: str):
        parsed = line.split(self.splitter)
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
    

class PositionalIndex(Index):
    def __init__(self) -> None:
        self.location = "final_positional_index.txt"
        self.index = defaultdict(defaultdict(list))
        if not os.path.exists("final_positional_index.txt"):
            self.build_index()

    def build_index(self) -> None:
        page_index = 0
        for domain in os.scandir(self.path_to_pages):
            for page in os.scandir(domain.path):
                page_index += 1 # enumerate vs hash ???
                with open(page.path, "r") as file:
                    data = json.loads(file.read())
                    html_content = data["content"]
                    text = BeautifulSoup(html_content, "lxml").get_text()
                    stems = self.tokenizer(text)
                    position = 0
                    for stem in stems:
                        position += 1
                        self.index[stem][page_index].append(position)
                print(page_index)
                if page_index % self.dump_threshold == 0: 
                    self.dump(f"positional_index{page_index//self.dump_threshold}.txt")
            
        self.dump(f"positional_index{page_index//self.dump_threshold + 1}.txt")
        self.merge_files()

    # not finished yet; need to add correct parsing        
    def dict_to_str(self, iid: dict[int, list[(int, int)]]):
        res = ""
        for k in sorted(iid):
            v = ",".join([str(i) for i in iid[k]])
            res += str(k) + self.splitter + v + "\n"
        return res

    def str_to_dict(self, line: str):
        parsed = line.split(self.splitter)
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


def build_index_of_index(inverted_index: Index):
    token_loc = {}
    with open(inverted_index.location, encoding="utf-8") as f:
        line = f.readline()
        while line: 
            info = line.split(inverted_index.splitter)
            token_loc[info[0]] = f.tell() - len(line) - 1
            line = f.readline()
    return token_loc

def find_token(token, token_loc, inverted_index: Index):
    line = ''
    with open(inverted_index.location, encoding="utf-8") as f:
        f.seek(token_loc[token])
        line = f.readline()
        
    return line
            

if __name__ == "__main__":
    iid = InvertedIndex()
    #ipd = PositionalIndex()
    