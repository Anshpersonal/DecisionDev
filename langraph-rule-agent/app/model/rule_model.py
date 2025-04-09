# app/model/rule_model.py

from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class Tool(BaseModel):
    """Model representing a decision service tool"""
    engine: str
    toolName: str
    toolDescription: str
    toolPath: str
    args: List[Dict[str, str]]
    output: str
    keywords: Optional[List[str]] = None

class ValidationRule(BaseModel):
    """Model representing a validation rule"""
    rule_text: str
    form_type: str

class ValidationResult(BaseModel):
    """Model representing validation results"""
    valid: bool = False
    validation_results: List[Dict[str, Any]] = []
    
    def get_formatted_response(self, form_type: str) -> str:
        """Generate human-readable response from validation results"""
        if self.valid:
            return f"✅ The {form_type} form has passed all validation rules."
        else:
            invalid_fields = []
            for result in self.validation_results:
                if not result.get("pass", False):
                    invalid_fields.append(f"❌ {result.get('rule', '')}: {result.get('reason', '')}")
            
            return f"The following issues were found in the {form_type} form:\n" + "\n".join(invalid_fields)