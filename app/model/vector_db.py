# app/models/vector_db.py - Vector database model

from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class VectorDatabase:
    """Model for interacting with the vector database"""
    
    def __init__(self, embeddings):
        """
        Initialize vector database
        
        Args:
            embeddings: Embedding model for vectorizing text
        """
        self.embeddings = embeddings
        self.db = None
    
    def initialize_db(self):
        """Create and populate vector database with validation rules"""
        # Example rules for different form types
        form_rules = {
            "renewals": [
               "Validate Owner Name must be present",
               "validate if owner Signature Date field is present",
                "validate if guarantee period field is present",
                "validate if contract number field is present",
                "validate if owner email address field is present",
                 "validate if owner phone number field is present"

            ],
            "withdrawals": [
                "Minimum age for loan application is 21 years",
                "Income verification must be present",
                "Contact information fields must be filled",
                "Loan amount must be specified and within valid range"
            ]
        }
        
        # Create document objects for vector storage
        documents = []
        for form_type, rules in form_rules.items():
            for rule in rules:
                documents.append(Document(
                    page_content=rule,
                    metadata={"form_type": form_type}
                ))
        
        # Create FAISS vector store
        self.db = FAISS.from_documents(documents, self.embeddings)
        
        print(f"Vector DB initialized with {len(documents)} rules")
        return self.db
    
    def retrieve_validation_rules(self, form_type):
        """
        Query the vector database for relevant validation rules
        
        Args:
            form_type (str): Type of the form
            
        Returns:
            list: List of validation rules
        """
        try:
            if not self.db:
                raise ValueError("Vector database not initialized")
                
            # Create a query embedding for the form type
            query = f"Validation rules for {form_type} form"
            
            # Search the vector database
            results = self.db.similarity_search_with_score(query, k=10)
            
            # Filter results by form type and minimum similarity
            filtered_rules = []
            for doc, score in results:
                if doc.metadata["form_type"] == form_type and score >= 0.7:
                    filtered_rules.append(doc.page_content)
            
            return filtered_rules if filtered_rules else ["No validation rules found for this form type"]
        
        except Exception as e:
            return [f"Error retrieving rules: {str(e)}"]