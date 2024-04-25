from langchain_openai import OpenAIEmbeddings
from base import BaseVectorizer
from dotenv import load_dotenv
import os

class VectorOpenai(BaseVectorizer):
    def __init__(self):
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.vectorizer = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    def run_model(self,query :str):
        response = self.vectorizer.embed_query(query)
        return response
    

    def run_model(self,query :list):
        response = self.vectorizer.embed_documents(query)
        return response

    def get_vectorizer(self):
        return self.vectorizer
    
    
