# app/service/api_service.py - Service for external API calls

import requests
import json

class APIService:
    """Service for making external API calls to fetch database records"""
    
    def __init__(self, base_url=None):
        """
        Initialize API service
        
        Args:
            base_url (str, optional): Base URL for API calls
        """
        self.base_url = base_url
    
    def fetch_policy_data(self, ContractNumber):
        """
        Fetch policy data from the database API
        
        Args:
            ContractNumber (str): ContractNumber to fetch
            
        Returns:
            dict: Policy data from database
        """
        try:
            # Construct the URL for the API call
            url = f"{self.base_url}api/lifecadservices/policy/mass/accountinfo?contractnumber={ContractNumber}" if self.base_url else f"/api/lifecadservices/policy/mass/accountinfo?contractnumber={ContractNumber}"
            
            # Make the API call
            response = requests.get(url)
            
            # Check for successful response
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}", "details": response.text}
            
        except Exception as e:
            return {"error": f"Error fetching policy data: {str(e)}"}
    
    def fetch_loan_data(self, loan_id):
        """
        Fetch loan data from the database API
        
        Args:
            loan_id (str): Loan ID to fetch
            
        Returns:
            dict: Loan data from database
        """
        try:
            # Construct the URL for the API call
            url = f"{self.base_url}/api/loans/{loan_id}" if self.base_url else f"/api/loans/{loan_id}"
            
            # Make the API call
            response = requests.get(url)
            
            # Check for successful response
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}", "details": response.text}
            
        except Exception as e:
            return {"error": f"Error fetching loan data: {str(e)}"}
    
    def fetch_data_by_form_type(self, form_type, id_value):
        """
        Fetch data based on form type and ID
        
        Args:
            form_type (str): Type of form
            id_value (str): ID value to use for lookup
            
        Returns:
            dict: Data from database
        """
        if form_type == "renewals":
            return self.fetch_policy_data(id_value)
        elif form_type == "withdrawals":
            return self.fetch_loan_data(id_value)
        else:
            return {"error": f"Unsupported form type for API fetch: {form_type}"}