# Names: Jacob Lee Kyuho Oh Aali Bin Rehan

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
import os

PATH_TO_PAGES = 'DEV'

class Index:
    def __init__(self) -> None:
        self.partial_indexes = []
        self.index = defaultdict(list)
        self.dump_threshold = 15000
        self.location = ""
        self.splitter = "#$%^&"
        self.token_loc = {}
    
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

    def build_index_of_index(self):
        with open(self.location, encoding="utf-8") as f:
            line = f.readline()
            while line: 
                info = line.split(self.splitter)
                self.token_loc[info[0]] = f.tell() - len(line) - 1
                line = f.readline()

    def find_token(self, token) -> dict:
        line = ''
        with open(self.location, encoding="utf-8") as f:
            f.seek(self.token_loc[token])
            line = f.readline()
        return self.str_to_dict(line)


class InvertedIndex(Index):
    def __init__(self) -> None:
        super().__init__()
        self.location = "final_index.txt"

    def add_page(self, stems, page_index) -> None:
        position = 0
        temp_index = {}
        if page_index % self.dump_threshold == 0: 
            self.dump(f"inverted_index{len(self.partial_indexes)}.txt")
            self.index = defaultdict(list)
        for stem in stems:
            position += 1
            if stem not in temp_index:
                temp_index[stem].extend([page_index, 1, position])
            else:
                temp_index[stem][1] += 1
                temp_index[stem].append(position)
        for stem in temp_index:
            self.index[stem] = tuple(temp_index[stem])

        # check accumulated index size with sys.getsizeof(index)
        # if it is over some threshold, dump it into a text file
        # maybe we can add try/except in the case of memory overflow - MemoryError in python 

    def merge_partials(self):
        self.dump(f"inverted_index{len(self.partial_indexes)}.txt")
        self.index = defaultdict(list)
        self.merge_files()
            
            
    def dict_to_str(self, iid: dict[str, list[(int, int)]]):
        res = ""
        for k in sorted(iid):
            v = ",".join([str(i) for i in iid[k]])
            res += str(k) + self.splitter + v + "\n"
        return res

    def str_to_dict(self, line: str):
        parsed = line.split(self.splitter)
        posting = []
        s = parsed[1]
        i = 0
        while i < len(parsed[1]):
            if s[i] == "(":
                res = ""
                i += 1
                while s[i] != ")":
                    res += s[i]
                    i += 1          
                tup = res.split(",")
                posting.append(tuple([int(tup[0]), float(tup[1])]))
            i += 1
        return {parsed[0]: posting}


# class PositionalIndex(Index):
#     # { token : [{docid : [positions]}]}
#     def __init__(self) -> None:
#         self.location = "final_positional_index.txt"
#         self.index = defaultdict(defaultdict(list))
#         if not os.path.exists("final_positional_index.txt"):
#             self.build_index()

#     def build_index(self) -> None:
#         pass
#         # position = 0
#         # for stem in stems:
#         #     position += 1
#         #     self.index[stem][page_index].append(position)
#         # print(page_index)
#         # if page_index % self.dump_threshold == 0: 
#         #     self.dump(f"positional_index{page_index//self.dump_threshold}.txt")
            
#         # self.dump(f"positional_index{page_index//self.dump_threshold + 1}.txt")
#         # self.merge_files()

#     # not finished yet; need to add correct parsing 
#     # token #splitter# docid : pos1, pos2, pos3 # docid : pos1, pos2, pos3 \n
#     def dict_to_str(self, iid: dict[str, dict[int, list[int]]]):
#         res = ""
#         for token in sorted(iid):
#             res += token + self.splitter
#             for dict in iid[token]:
#                 for k in dict:
#                     v = ",".join([str(i) for i in dict[k]])
#                 res += str(k) + ":" + v + "#"
#             res += '\n'
#         return res

#     def str_to_dict(self, line: str):
#         parsed = line.split(self.splitter)
#         posting = []
#         s = parsed[1]
#         docid = ""
#         i = 0
#         while i < len(parsed[1]):
#             if s[i] == ":":
#                 pos_list = ""
#                 i += 1 
#                 while s[i] != "#":     
#                     pos_list += s[i]
#                     i += 1 
#                 posting.append({int(docid) : [int(x) for x in pos_list.split(",")]})
#                 docid = ""
#                 i += 1
#             docid += s[i]
#             i += 1
#         return {parsed[0]: posting}

class BigramIndex(Index):

    def __init__(self):
        Index.__init__()
        self.location = "bigram_index.txt"

    def add_page(self, stemmed_tokens, doc_id):
        token_bigrams = nltk.bigrams(stemmed_tokens)
        bigram_count = Counter(token_bigrams)
        for bigram, frequency in bigram_count.items():
            self.index[bigram].append((doc_id, frequency))

        if doc_id % self.dump_threshold == 0:
            self.dump(f"bigram_partial{len(self.partial_indexes) + 1}.txt")
            self.index = defaultdict(list)

    def merge_partials(self):
        self.dump(f"bigram_partial{len(self.partial_indexes) + 1}.txt")
        self.index = defaultdict(list)
        self.merge_files()

    def dict_to_str(self, bigram_index: dict[tuple(str, str), list[(int, int)]]):
        result = ""
        for bigram in sorted(bigram_index):
            postings = "#@#".join(f"{doc_id},{freq}" for doc_id, freq in bigram_index[bigram])
            bigram_string = f"{bigram[0]} {bigram[1]}"
            result += bigram_string + self.splitter + postings + "\n"
        return result

    def str_to_dict(self, line: str):
        line = line.rstrip()
        splitted = line.split(self.splitter)
        bigram = tuple(splitted[0].split())
        postings_str = [posting.split(",") for posting in splitted[1].split("#@#")]
        parsed_postings = []
        for posting in postings_str:
            doc_id = int(posting[0])
            freq = int(posting[1])
            parsed_postings.append(tuple(doc_id, freq))
        return {bigram: parsed_postings}
    
class TrigramIndex(Index):

    def __init__(self):
        Index.__init__()
        self.location = "trigram_index.txt"

    def add_page(self, stemmed_tokens, doc_id):
        token_trigrams = nltk.trigrams(stemmed_tokens)
        bigram_count = Counter(token_trigrams)
        for trigram, frequency in bigram_count.items():
            self.index[trigram].append((doc_id, frequency))

        if doc_id % self.dump_threshold == 0:
            self.dump(f"trigram_partial{len(self.partial_indexes) + 1}.txt")
            self.index = defaultdict(list)

    def merge_partials(self):
        self.dump(f"trigram_partial{len(self.partial_indexes) + 1}.txt")
        self.index = defaultdict(list)
        self.merge_files()

    def dict_to_str(self, trigram_index: dict[tuple(str, str), list[(int, int)]]):
        result = ""
        for trigram in sorted(trigram_index):
            postings = "#@#".join(f"{doc_id},{freq}" for doc_id, freq in trigram_index[trigram])
            bigram_string = f"{trigram[0]} {trigram[1]} {trigram[2]}"
            result += bigram_string + self.splitter + postings + "\n"
        return result
    
    def str_to_dict(self, line: str):
        line = line.rstrip()
        splitted = line.split(self.splitter)
        trigram = tuple(splitted[0].split())
        postings_str = [posting.split(",") for posting in splitted[1].split("#@#")]
        parsed_postings = []
        for posting in postings_str:
            doc_id = int(posting[0])
            freq = int(posting[1])
            parsed_postings.append(tuple(doc_id, freq))
        return {trigram: parsed_postings}

            
def build_indexes():
    # initialize all indexes
    iid = InvertedIndex()
    bigram_index = BigramIndex()
    trigram_index = TrigramIndex()
    
    page_index = 0
    urls = {}
    for domain in os.scandir(PATH_TO_PAGES):
        for page in os.scandir(domain.path):
            page_index += 1 # enumerate vs hash ???
            with open(page.path, "r") as file:
                data = json.loads(file.read())
                html_content = data["content"]
                urls[page_index] = data["url"]
                text = BeautifulSoup(html_content, "lxml").get_text()
                iid_stems = iid.tokenizer(text)
                iid.add_page(iid_stems, page_index)
                # add more
    dumping_urls = json.dumps(urls)
    with open("urlindex.json", "w") as url_index:
        url_index.write(dumping_urls)
    return iid

if __name__ == "__main__":
    iid = InvertedIndex()
    #ipd = PositionalIndex()
    