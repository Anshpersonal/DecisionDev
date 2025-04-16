# app/service/rag_service.py - Updated for FAISS with separate OCR and DB vector stores
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

class RAGService:
    """
    Service for Retrieval-Augmented Generation using FAISS.
    This version maintains two separate vector stores:
      - One for OCR data
      - One for DB data
    It uses the OpenAI embeddings model "text-embedding-ada-002" for embedding.
    """
    
    def __init__(self, llm):
        """
        Initialize the RAGService.
        
        Args:
            llm: The LLM to be used in retrieval-augmented generation.
        """
        self.llm = llm
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=30)
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
        # Two separate vector stores: one for OCR data, one for DB data.
        self.ocr_vector_store = None
        self.db_vector_store = None
        
    def document_to_dict(self, doc):
        """
        Convert a Document object to a JSON-serializable dictionary.
        
        Args:
            doc: A Document object
            
        Returns:
            dict: A JSON-serializable dictionary representation of the Document
        """
        return {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }

    def ingest_ocr_text(self, text: str, metadata: dict = None) -> bool:
        """
        Ingest OCR text into the OCR vector store.
        
        Args:
            text (str): The OCR text to embed.
            metadata (dict, optional): Additional metadata to store.
        
        Returns:
            bool: True if ingestion was successful, False otherwise.
        """
        if metadata is None:
            metadata = {}
            print("2.01")
        try:
            print("2.1")
            doc = Document(page_content=text, metadata=metadata)
            chunks = self.text_splitter.split_documents([doc])
            print("2.2")
            if not self.ocr_vector_store:
                print("2.3")
                self.ocr_vector_store = FAISS.from_documents(chunks, self.embedding_model)
            else:
                print("2.4")
                self.ocr_vector_store.add_documents(chunks)
            return True
        except Exception as e:
            print(f"Error in ingest_ocr_text: {e}")
            return False

    def ingest_db_text(self, text: str, metadata: dict = None) -> bool:
        """
        Ingest DB text into the DB vector store.
        
        Args:
            text (str): The DB text to embed.
            metadata (dict, optional): Additional metadata to store.
        
        Returns:
            bool: True if ingestion was successful, False otherwise.
        """
        print("2.01")
        if metadata is None:
            metadata = {}
        try:
            doc = Document(page_content=text, metadata=metadata)
            chunks = self.text_splitter.split_documents([doc])
            print("2.1")
            if not self.db_vector_store:
                self.db_vector_store = FAISS.from_documents(chunks, self.embedding_model)
                print("2.2")
            else:
                self.db_vector_store.add_documents(chunks)

            return True
        except Exception as e:
            print(f"Error in ingest_db_text: {e}")
            return False

    def retrieve_ocr(self, query: str, k: int = 5):
        """
        Retrieve relevant OCR data from the OCR vector store.
        
        Args:
            query (str): The query to search for.
            k (int, optional): Number of results to return. Defaults to 5.
        
        Returns:
            list: JSON-serializable retrieval results from the OCR vector store.
        """
        if not self.ocr_vector_store:
            return []
        try:
            retriever = self.ocr_vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 1, "score_threshold": 0.1}
            )
            # Use invoke instead of get_relevant_documents
            docs = retriever.invoke(query)
            # Convert Document objects to dictionaries
            return [self.document_to_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Error in retrieve_ocr: {e}")
            return []
    
    def retrieve_db(self, query: str, k: int = 5):
        """
        Retrieve relevant DB data from the DB vector store.
        
        Args:
            query (str): The query to search for.
            k (int, optional): Number of results to return. Defaults to 5.
        
        Returns:
            list: JSON-serializable retrieval results from the DB vector store.
        """
        if not self.db_vector_store:
            return []
        try:
            retriever = self.db_vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 8, "score_threshold": 0.5}
            )
            # Use invoke instead of get_relevant_documents
            docs = retriever.invoke(query)
            # Convert Document objects to dictionaries
            return [self.document_to_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Error in retrieve_db: {e}")
            return []
    
    def generate_response(self, query: str, context: list):
        """
        Generate a response using the LLM with the provided context.
        
        Args:
            query (str): The user query
            context (list): List of relevant documents to use as context
            
        Returns:
            str: The generated response
        """
        try:
            # Format context for the LLM
            formatted_context = "\n\n".join([doc["page_content"] for doc in context])
            
            # Create prompt with context
            prompt = f"""
            Context information:
            {formatted_context}
            
            Based on the context information, please answer the following question:
            {query}
            """
            
            # Generate response using the LLM
            response = self.llm.invoke(prompt)
            
            return response
        except Exception as e:
            print(f"Error in generate_response: {e}")
            return f"Error generating response: {str(e)}"
    
    def clear(self):
        """
        Clear both OCR and DB vector stores.
        """
        self.ocr_vector_store = None
        self.db_vector_store = None