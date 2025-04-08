# app/services/validation_service.py - Validation service for form data

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.model.rule_model import ValidationResult

class ValidationService:
    """Service for validating extracted form data against rules"""
    
    def __init__(self, llm_model):
        """
        Initialize validation service
        
        Args:
            llm_model: LLM model for validation
        """
        self.model = llm_model
    
    def validate_form_data(self, json_data, rules, form_type):
        """
        Validate JSON data against rules using LLM
        
        Args:
            json_data (dict): Extracted form data
            rules (list): List of validation rules
            form_type (str): Type of form being validated
            
        Returns:
            ValidationResult: Result of the validation
        """
        try:
            # Create validation prompt
            validation_prompt = ChatPromptTemplate.from_template(
                """
                You are an AI agent validating form data against business rules.
                
                Form Data (extracted from OCR):
                {json_data}
                
                Validation Rules:
                {rules}
                
                For each rule, validate the extracted form data for rule
                For each rule:
                1. Determine if the rule passes or fails
                2. Provide a clear reason if it fails
                
                Output a JSON with this structure:
                {{
                    "valid": boolean,  // true if all rules pass
                    "validation_results": [
                        {{
                            "rule": "string",  // the rule being checked
                            "pass": boolean,   // true if passes, false if fails
                            "reason": "string" // explanation (only needed for failures)
                        }}
                    ]
                }}
                do not be too much precise for the rules validation
                """
            )
            
            # Create chain with JSON output parser
            json_parser = JsonOutputParser()
            validation_chain = validation_prompt | self.model | json_parser
            
            # Invoke the validation chain
            validation_result = validation_chain.invoke({
                "json_data": str(json_data),
                "rules": "\n".join(rules)
            })
            
            # Convert to ValidationResult model
            result = ValidationResult.from_dict(validation_result)
            return result
        
        except Exception as e:
            # Return error validation result
            result = ValidationResult(valid=False)
            result.validation_results = [{
                "rule": "System Error",
                "pass": False,
                "reason": f"Validation error: {str(e)}"
            }]
            return result