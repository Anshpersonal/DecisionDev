# app/service/comparison_service.py - Service for comparing OCR data with DB data

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class ComparisonService:
    """Service for comparing OCR-extracted data with database data"""
    
    def __init__(self, llm_model):
        """
        Initialize comparison service
        
        Args:
            llm_model: LLM model for comparison
        """
        self.model = llm_model
    
    def compare_data(self, ocr_data, db_data, form_type):
        """
        Compare OCR-extracted data with database data using LLM
        
        Args:
            ocr_data (dict): Data extracted from OCR
            db_data (dict): Data fetched from database
            form_type (str): Type of form being validated
            
        Returns:
            dict: Result of the comparison
        """
        try:
            # Create comparison prompt
            comparison_prompt = ChatPromptTemplate.from_template(
                """
                You are an AI agent comparing data extracted from a form using OCR with 
                data retrieved from a database.
                
                OCR-Extracted Data:
                {ocr_data}
                
                Database Data:
                {db_data}
                
                KEEP BELOW POINTS IN MIND

               1. Make sure to Compare only the common fields present in both the data, ignore fields which are not common.

               2. In reasoning also generate a id for invalid validation and named it as NIGO_ID

               3. SIgnore commas if it is there in fields like name , also do not give note of it while giving json response.
                
                Output a JSON with this structure:
                {{
                    "matches": boolean,  // true if all fields have match field true
                    "comparison_results": [
                        {{
                            "field": "string",     // field name
                            "ocr_value": "string", // value from OCR
                            "db_value": "string",  // value from database
                            "match": boolean,      // true if values match
                            "note": "string"       // explanation (only for mismatches)
                        }}
                    ]
                }}
               
                """
            )
            
            # Create chain with JSON output parser
            json_parser = JsonOutputParser()
            comparison_chain = comparison_prompt | self.model | json_parser
            
            # Invoke the comparison chain
            comparison_result = comparison_chain.invoke({
                "ocr_data": str(ocr_data),
                "db_data": str(db_data),
                "form_type": form_type
            })
            
            return comparison_result
        
        except Exception as e:
            # Return error comparison result
            return {
                "matches": False,
                "comparison_results": [{
                    "field": "System Error",
                    "ocr_value": "",
                    "db_value": "",
                    "match": False,
                    "note": f"Comparison error: {str(e)}"
                }],
                "error": str(e)
            }