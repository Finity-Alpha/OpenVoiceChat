# from openai import OpenAI
from dotenv import load_dotenv
from base import BaseChatbot
import queue
import os
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
import langchain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.redis import Redis
from langchain_openai import ChatOpenAI
from redisvl.extensions.llmcache import SemanticCache
from redisvl.utils.vectorize import OpenAITextVectorizer
from redisvl.utils.vectorize import HFTextVectorizer


load_dotenv()
os.environ['OPENAI_API_KEY'] = "your-api-key"
api_key = os.getenv("OPENAI_API_KEY") 

def get_db_vectorizer():
    vectorizer = OpenAIEmbeddings(api_key=api_key)
    return vectorizer

def get_cache_vectorizer():
    vectorizer = HFTextVectorizer(model="sentence-transformers/all-mpnet-base-v2")
    return vectorizer

def get_llm():
    llm = ChatOpenAI(model='gpt-3.5-turbo',openai_api_key=api_key)
    return llm


def load_pdf(file_path):
    with open(file_path, 'rb') as f:
        t=""
        pdf_reader = pypdf.PdfReader(f)
        num_pages = pdf_reader._get_num_pages()
        # You can access each page like this:
        for page_num in range(num_pages):
            page = pdf_reader._get_page(page_num)
            # Do something with the page
            text = page.extract_text()
            t=t+text.strip()
    return t
    

class Chatbot_rag(BaseChatbot):
    def __init__(self,Model='gpt-3.5-turbo'):
        self.embedding= get_db_vectorizer()
        self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 150
        )
        self.vectordb = Redis.from_texts(
        texts=[''],
        embedding = self.embedding,
        redis_url="redis://localhost:6379/"
        )
        
        hf = get_cache_vectorizer()
        self.semantic_cache = SemanticCache(
        name="ntest",                    
        prefix="ntest",                   
        redis_url="redis://localhost:6379",
        distance_threshold=0.1,
        vectorizer=hf
        )
        self.start_llm()
        print("setup complete")
        return 
    
    def use_pdf(self,file_name: str):
        text = load_pdf(file_name)
        self.add_to_vectordb(text)
        return
    
    def add_to_vectordb(self,text):
        splits = self.text_splitter.split_text(text)  
        self.vectordb.add_texts(splits)
        return
    
    def start_llm(self):
        self.llm = get_llm()
        self.mretriever = self.vectordb.as_retriever(search_type="similarity", search_kwargs={"distance_threshold": 0.8})
        template = """Use the following pieces of context given inside ``` to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
        {context}
        Question: {question}
        Helpful Answer:"""
    
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template) 
        self.qa_chain= RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.mretriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        return
    
    
    def check_cache(self,ques: str):
        if answer := self.semantic_cache.check(prompt=ques,return_fields=["prompt", "response", "metadata"],):
            return answer[0]
        return 0
    
    def set_cache(self,ques,result):
        self.semantic_cache.store(
            prompt=ques,
            response=result,
        )
    
    def run(self, input_text):
        result = self.check_cache(input_text)  
        result==0
        if result==0:    
            chunk = self.qa_chain.invoke({"query": input_text})
            # for chunk in stream:
            if chunk is not None:
                print("###",chunk['result'])
                return chunk['result']
        else:
            return result['response']
        

    def post_process(self, response):
        return response


if __name__ == "__main__":
    preprompt = 'You are a helpful assistant.'
    john = Chatbot_rag()
    # john.use_pdf("../uploads/data.pdf")
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)
        print(response)
