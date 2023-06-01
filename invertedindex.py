# Names: Jacob Lee Kyuho Oh Aali Bin Rehan

from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import nltk
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
import os
import duplicatecheck

PATH_TO_PAGES = 'DEV'

class Index:
    def __init__(self) -> None:
        self.partial_indexes = []
        self.index = defaultdict(list)
        self.dump_threshold = 15000
        self.location = ""
        self.splitter = "#$%^&"
        self.token_loc = {}
    
    def stemmer(self, tokens: list[str]):
        # tokens = word_tokenize(content)
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(token) for token in tokens]
        return stemmed_words
    
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
        self.location = "final_index1.txt"

    def add_page(self, stems, page_index) -> None:
        position = 0
        temp_index = defaultdict(list)
        if page_index % self.dump_threshold == 0: 
            self.dump(f"inverted_index{len(self.partial_indexes)}.txt")
            self.index = defaultdict(list)
        for stem in stems:
            position += 1
            if stem not in temp_index:
                temp_index[stem] = [page_index, 1, position]
            else:
                temp_index[stem][1] += 1
                temp_index[stem].append(position)
        for stem in temp_index:
            self.index[stem].append(tuple(temp_index[stem]))

        # check accumulated index size with sys.getsizeof(index)
        # if it is over some threshold, dump it into a text file
        # maybe we can add try/except in the case of memory overflow - MemoryError in python 

    def merge_partials(self):
        self.dump(f"inverted_index{len(self.partial_indexes)}.txt")
        self.index = defaultdict(list)
        self.merge_files()
            
            
    def dict_to_str(self, iid: dict[str, list[(int, int)]]):
        res = []
        for k in sorted(iid):
            v = ",".join([str(i) for i in iid[k]])
            res.append(str(k) + self.splitter + v + "\n")
        return ''.join(res)

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
                tup = [int(x) for x in res.split(",")]
                posting.append(tuple(tup))
            i += 1
        return {parsed[0]: posting}

class BigramIndex(Index):

    def __init__(self):
        Index.__init__(self)
        self.location = "bigram_index.txt"
        self.dump_threshold = 10000

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

    def dict_to_str(self, bigram_index: dict[tuple[str, str], list[(int, int)]]):
        result = []
        for bigram in sorted(bigram_index):
            postings = "#@#".join(f"{doc_id},{freq}" for doc_id, freq in bigram_index[bigram])
            bigram_string = f"{bigram[0]} {bigram[1]}"
            result.append(bigram_string + self.splitter + postings + "\n")
        return ''.join(result)

    def str_to_dict(self, line: str):
        line = line.rstrip()
        splitted = line.split(self.splitter)
        bigram = tuple(splitted[0].split())
        postings_str = [posting.split(",") for posting in splitted[1].split("#@#")]
        parsed_postings = []
        for posting in postings_str:
            doc_id = int(posting[0])
            freq = int(posting[1])
            parsed_postings.append((doc_id, freq))
        return {bigram: parsed_postings}
    
    def build_index_of_index(self):
        with open(self.location, encoding="utf-8") as f:
            line = f.readline()
            while line: 
                info = line.split(self.splitter)
                token = tuple(info[0].split())
                self.token_loc[token] = f.tell() - len(line) - 1
                line = f.readline()

    def find_token(self, token) -> dict:
        line = ''
        with open(self.location, encoding="utf-8") as f:
            f.seek(self.token_loc[token])
            line = f.readline()
        return self.str_to_dict(line)
    
class TrigramIndex(Index):

    def __init__(self):
        Index.__init__(self)
        self.location = "trigram_index.txt"
        self.dump_threshold = 10000

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

    def dict_to_str(self, trigram_index: dict[tuple[str, str], list[(int, int)]]):
        result = []
        for trigram in sorted(trigram_index):
            postings = "#@#".join(f"{doc_id},{freq}" for doc_id, freq in trigram_index[trigram])
            bigram_string = f"{trigram[0]} {trigram[1]} {trigram[2]}"
            result.append(bigram_string + self.splitter + postings + "\n")
        return ''.join(result)
    
    def str_to_dict(self, line: str):
        line = line.rstrip()
        splitted = line.split(self.splitter)
        trigram = tuple(splitted[0].split())
        postings_str = [posting.split(",") for posting in splitted[1].split("#@#")]
        parsed_postings = []
        for posting in postings_str:
            doc_id = int(posting[0])
            freq = int(posting[1])
            parsed_postings.append((doc_id, freq))
        return {trigram: parsed_postings}
    
    def build_index_of_index(self):
        with open(self.location, encoding="utf-8") as f:
            line = f.readline()
            while line: 
                info = line.split(self.splitter)
                token = tuple(info[0].split())
                self.token_loc[token] = f.tell() - len(line) - 1
                line = f.readline()

    def find_token(self, token) -> dict:
        line = ''
        with open(self.location, encoding="utf-8") as f:
            f.seek(self.token_loc[token])
            line = f.readline()
        return self.str_to_dict(line)

            
def build_indexes():
    # initialize all indexes
    iid = InvertedIndex()
    bigram_index = BigramIndex()
    trigram_index = TrigramIndex()
    
    page_index = 0
    urls = {}
    dup_pages = []
    tokenizer = RegexpTokenizer(r'\w+')
    for domain in os.scandir(PATH_TO_PAGES):
        simhash_values = []
        # if domain.name != "www_informatics_uci_edu":
        #     continue
        for page in os.scandir(domain.path):
            with open(page.path, "r") as file:
                data = json.loads(file.read())
                html_content = data["content"]
                text = BeautifulSoup(html_content, "lxml").get_text()
                tokens = tokenizer.tokenize(text)

                # dup check goes here
                hash_value = duplicatecheck.hash(Counter(tokens))
                is_duplicate = duplicatecheck.duplicate_exists(hash_value, simhash_values)
                simhash_values.append(hash_value)
                # if is_duplicate:
                #     dup_pages.append(data["url"])
                # else:
                if not is_duplicate:
                    page_index += 1 # enumerate vs hash ???
                    urls[page_index] = data["url"]
                    print(page_index)
                    stems = iid.stemmer(tokens)
                    iid.add_page(stems, page_index)
                    bigram_index.add_page(stems, page_index)
                    trigram_index.add_page(stems, page_index)
                # add more
        #         if page_index >= 3000:
        #             break

        # if page_index >= 3000:
        #     break

    iid.merge_partials()
    bigram_index.merge_partials()
    trigram_index.merge_partials()
    dumping_urls = json.dumps(urls)
    with open("urlindex.json", "w") as url_index:
        url_index.write(dumping_urls)
    # print(dup_pages)

if __name__ == "__main__":
    iid = InvertedIndex()
    #ipd = PositionalIndex()
    