from langchain_community.embeddings import HuggingFaceEmbeddings
# from base import BaseVectorizer
from .base import BaseVectorizer
from dotenv import load_dotenv
import os


class VectorHf(BaseVectorizer):
    def __init__(self):
        self.model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        self.vectorizer =   HuggingFaceEmbeddings(
                            model_name=self.model_name,
                            model_kwargs=model_kwargs,
                            encode_kwargs=encode_kwargs
                            )


    def run_model(self,query :str):
        response = self.vectorizer.embed_query(query)
        return response
    
    def run_model(self,query :list):
        response = self.vectorizer.embed_documents(query)
        return response
    
    
    def get_vectorizer(self):
        return self.vectorizer
    
    
if __name__ == "__main__":
    vec = VectorHf()
    print("complete")
    print(vec.run_model("hello"))
    print("next is: ")
    print(vec.run_model(['hello','world']))