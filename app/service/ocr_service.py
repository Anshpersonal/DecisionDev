# app/services/ocr_service.py - OCR service for form data extraction

import requests
import os
import json

class OCRService:
    """Service for extracting data from forms using OCR"""
    
    def __init__(self, api_endpoint):
        """
        Initialize OCR service
        
        Args:
            api_endpoint (str): Endpoint for OCR API
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
            # In a production environment, you'd upload the file to the OCR API
            # For now, we'll simulate by trying to fetch from the path directly
            # response = requests.get(file_path)
            return file_path 
            # if response.status_code == 200:
            #     return response.json()
            # else:
            #     return {"error": f"OCR API error: {response.status_code}", "details": response.text}
            
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
                # "Name": "sarams sarn",
                # "Policy Type": "Health Insurance",
                # "ContractNumber": "571003597",
                "SourceSystem": "LC",
                "ContractNumber": "571003597",
                "ContractId": "269430",
                "CovId": "0",
                "OwnerName": "sarams, sarn",
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
            return {"error": "Unsupported test form type"}