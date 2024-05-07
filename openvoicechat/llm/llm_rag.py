from .base import BaseChatbot
import os
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import langchain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
import pypdf
class Chatbot_rag(BaseChatbot):
    def __init__(self, sys_prompt='',
                 Model='gpt-3.5-turbo',
                 api_key=''):
        self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
        )
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = Chroma.from_texts(texts=[''],embedding=self.embedding_function)
        self.llm = llm = OpenAI(openai_api_key=api_key)
        self.use_pdf('uploads/data.pdf')
        self.start_llm()

    def load_pdf(self,file_path):
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
    
    def use_pdf(self,file_name: str):
        text = self.load_pdf(file_name)
        self.add_to_vectordb(text)
        return 

    def add_to_vectordb(self,text):
        splits = self.text_splitter.split_text(text)  
        self.db.add_texts(splits)
        return
    
    def start_llm(self):
        self.mretriever = self.db.as_retriever()
        template = """Give answers using following pieces of context given inside ``` to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
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

    def run(self, input_text):
        result = self.qa_chain({"query": input_text})
        yield result['result']

    def post_process(self, response):
        return response


if __name__ == "__main__":
    preprompt = 'You are a helpful assistant.'
    john = Chatbot_rag(sys_prompt=preprompt)
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)

        print(response)
