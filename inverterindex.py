class InvertedIndexToken:
    def __init__(self, token: str, docId: list):
        self.token = token
        self.docId = docId
    
    def add_docId(self, newId):
        for i,doc in enumerate(self.docId):
            if doc < newId:
                continue
        self.docId = self.docId[:i-1] + [newId]  + self.docId[i:]
    
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


def tokenizer():
    pass
