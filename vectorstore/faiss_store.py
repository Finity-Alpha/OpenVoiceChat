from base import VectorStore
from vectorizer .vector_hf import VectorHf
from langchain_community.vectorstores.faiss import FAISS
class VectorStoreFaiss(VectorStore):
    def __init__(self):
        self.vectorizer = self.getVectorizer()
        self.db = FAISS.from_texts([''], self.vectorizer)
        
    def getVectorizer(self):
        vectorizer = VectorHf().get_vectorizer()
        return vectorizer

    
    def ingest_docs(self,docs :list):
        self.db.add_documents(docs)
        return
    
    def ingest_text(self, text: str):
        self.db.add_texts([text])
        return
    
    def top_k_docs(self,query: str,num=2):
        return self.db.similarity_search(query,num)
    
    def top_k_texts(self,query: str,num=2):
        rt = self.db.similarity_search(query,num)
        text=""
        for i in rt:
            text=text+i.page_content
        return text
    
    
     


if __name__ == "__main__":
    vs = VectorStoreFaiss()
    
    while(True):
        vs.ingest_text(input("ENter: "))
        print(vs.top_k_texts(input("enter to find")))