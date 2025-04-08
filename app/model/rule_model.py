# app/models/rule_model.py - Validation rules model

class ValidationRule:
    """Model representing a validation rule"""
    
    def __init__(self, rule_text, form_type):
        """
        Initialize validation rule
        
        Args:
            rule_text (str): Text description of the rule
            form_type (str): Type of form this rule applies to
        """
        self.rule_text = rule_text
        self.form_type = form_type
    
    def to_dict(self):
        """Convert rule to dictionary"""
        return {
            "rule_text": self.rule_text,
            "form_type": self.form_type
        }


class ValidationResult:
    """Model representing validation results"""
    
    def __init__(self, valid=False, validation_results=None):
        """
        Initialize validation result
        
        Args:
            valid (bool): Whether validation passed
            validation_results (list): Detailed validation results
        """
        self.valid = valid
        self.validation_results = validation_results or []
    
    def to_dict(self):
        """Convert validation result to dictionary"""
        return {
            "valid": self.valid,
            "validation_results": self.validation_results
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create ValidationResult from dictionary"""
        instance = cls(valid=data.get("valid", False))
        instance.validation_results = data.get("validation_results", [])
        return instance
    
    def get_formatted_response(self, form_type):
        """Generate human-readable response from validation results"""
        if self.valid:
            return f"✅ The {form_type} form has all fields filled correctly."
        else:
            invalid_fields = []
            for result in self.validation_results:
                if not result.get("pass", False):
                    invalid_fields.append(f"❌ {result.get('rule', '')}: {result.get('reason', '')}")
            
            return f"The following issues were found in the {form_type} form:\n" + "\n".join(invalid_fields)