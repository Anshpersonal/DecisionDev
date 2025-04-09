# app/service/rag_service.py - Service for RAG capabilities

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores.utils import filter_complex_metadata
import os
from langchain.schema.document import Document
from app.config import Config

config = Config()

class RAGService:
    """Service for Retrieval-Augmented Generation"""
    
    def __init__(self, llm):
        """
        Initialize RAG service
        
        Args:
            llm: LLM model for RAG
        """
        self.llm = llm
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template(
            """
            You are an AI assistant that helps answer questions based on the provided context.
            
            Context:
            {context}
            
            Question:
            {input}
            
            If the answer is not in the context, just say that you don't know. 
            Keep your answer concise and to the point.
            
            Answer:
            """
        )
        self.vector_store = None
        self.retriever = None
        self.chain = None
    
    def ingest_document(self, pdf_file_path):
        """
        Ingest a PDF document into the vector store
        
        Args:
            pdf_file_path (str): Path to the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            docs = PyPDFLoader(file_path=pdf_file_path).load()
            chunks = self.text_splitter.split_documents(docs)
            chunks = filter_complex_metadata(chunks)
            
            if not self.vector_store:
                # Initialize vector store if it doesn't exist
                self.vector_store = Chroma.from_documents(
                    documents=chunks, 
                    embedding=FastEmbedEmbeddings()
                )
            else:
                # Add documents to existing vector store
                self.vector_store.add_documents(chunks)
            
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": 3,
                    "score_threshold": 0.1,
                },
            )
            
            self.chain = (
                {"context": self.retriever, "input": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            return True
        except Exception as e:
            print(f"Error ingesting document: {e}")
            return False
    
    def ingest_text(self, text, metadata=None):
        """
        Ingest text directly into the vector store
        
        Args:
            text (str): Text to ingest
            metadata (dict, optional): Metadata for the text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not metadata:
                metadata = {}
                
            doc = Document(page_content=text, metadata=metadata)
            chunks = self.text_splitter.split_documents([doc])
            
            if not self.vector_store:
                # Initialize vector store if it doesn't exist
                self.vector_store = Chroma.from_documents(
                    documents=chunks, 
                    embedding=FastEmbedEmbeddings()
                )
            else:
                # Add documents to existing vector store
                self.vector_store.add_documents(chunks)
            
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": 3,
                    "score_threshold": 0.1,
                },
            )
            
            self.chain = (
                {"context": self.retriever, "input": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            return True
        except Exception as e:
            print(f"Error ingesting text: {e}")
            return False
    
    def ingest_documents_from_directory(self, directory_path):
        """
        Ingest all PDF documents from a directory
        
        Args:
            directory_path (str): Path to the directory
            
        Returns:
            int: Number of documents ingested
        """
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return 0
            
        count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                try:
                    if self.ingest_document(file_path):
                        count += 1
                        print(f"Ingested document: {filename}")
                except Exception as e:
                    print(f"Error ingesting {filename}: {e}")
        
        return count
    
    def process_query(self, query):
        """
        Process a query using RAG
        
        Args:
            query (str): User query
            
        Returns:
            str: Response to the query
        """
        if not self.chain:
            return "No documents have been loaded. Please add a document first."
        
        try:
            response = self.chain.invoke({"input": query})
            return response
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def clear(self):
        """Clear the vector store and chain"""
        self.vector_store = None
        self.retriever = None
        self.chain = None