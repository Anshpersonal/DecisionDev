# app/models/form_model.py - Form data model

class FormData:
    """Model representing form data and type"""
    
    def __init__(self, form_type, file_path=None, file_data=None):
        """
        Initialize form data
        
        Args:
            form_type (str): Type of form (e.g., 'Rewnewals', 'Withdrawals')
            file_path (str, optional): Path to the form file
            file_data (bytes, optional): Binary form data
        """
        self.form_type = form_type
        self.file_path = file_path
        self.file_data = file_data
        self.extracted_data = None
    
    def to_dict(self):
        """Convert form data to dictionary for processing"""
        return {
            "form_type": self.form_type,
            "file_path": self.file_path,
            "extracted_data": self.extracted_data
        }
    
    def set_extracted_data(self, data):
        """Set extracted data from OCR process"""
        self.extracted_data = data