# app/service/ocr_service.py - Service for OCR data extraction

class OCRService:
    """Service for extracting data from forms using OCR"""
    
    def __init__(self, api_endpoint=None):
        """
        Initialize OCR service
        
        Args:
            api_endpoint (str, optional): Endpoint for OCR API
        """
        self.api_endpoint = api_endpoint
    
    def extract_form_data(self, file_path):
        """
        Extract structured data from a form using the OCR API
        
        Args:
            file_path (str): Path to the form file
            
        Returns:
            dict: JSON data extracted from the form
        """
        try:
            # In a real implementation, this would call an OCR API
            # For now, we'll return a simplified response
            return {
                "extracted_data": f"Data extracted from {file_path}",
                "metadata": {
                    "file_path": file_path,
                    "page_count": 1
                }
            }
        except Exception as e:
            return {"error": f"Error processing form: {str(e)}"}
    
    def extract_test_data(self, form_type):
        """
        Generate test data for development and testing
        
        Args:
            form_type (str): Type of form to generate test data for
            
        Returns:
            dict: Simulated form data
        """
        if form_type == "renewals":
            return {
                "SourceSystem": "LC",
                "ContractNumber": "571003597",
                "ContractId": "269430",
                "CovId": "0",
                "OwnerName": "John Doe",
                "QualTypeCode": "Non-Qualified",
                "QualTypeDesc": "Non-Qualified",
                "APPLICATIONDATE": "2018-01-04T00:00:00",
                "ProductLine": "ANNUITY",
                "ModifiedEndowmentStatus": "0",
                "MaturityDate": "2050-01-01T00:00:00",
                "ProductCategory": "FIXED",
                "ProductName": "Stable Voyage",
                "IssueState": "KS",
                "IssueDate": "2018-01-04T00:00:00",
                "IssueAge": "58",
                "ContractStatus": "ACTIVE",
                "PlanCode": "571",
            }
        elif form_type == "withdrawals":
            return {
                "Name": "Jane Smith",
                "Age": "22",
                "Income": "$75,000",
                "Loan Amount": "$250,000",
                "Contact Phone": ""  # Missing contact info
            }
        else:
            return {
                "extracted_text": "This is sample extracted text from a document.",
                "metadata": {
                    "document_type": "generic"
                }
            }