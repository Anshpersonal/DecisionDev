# app/service/update_service.py - Service for updating external database

import requests
import json
import datetime

class UpdateService:
    """Service for updating external database via API"""
    
    def __init__(self, base_url=None):
        """
        Initialize update service
        
        Args:
            base_url (str, optional): Base URL for API calls
        """
        self.base_url = base_url
    
    def update_database(self, form_type, form_data, validation_result, comparison_result=None):
        """
        Send update to external database based on form data and validation
        
        Args:
            form_type (str): Type of form
            form_data (dict): Extracted form data
            validation_result (dict): Result of validation against rules
            comparison_result (dict, optional): Result of comparison with database
            
        Returns:
            dict: Result of the update operation
        """
        try:
            # Determine endpoint based on form type
            endpoint = f"/api/{form_type}s/update"  # For endpoints like /api/insurances/update or /api/loans/update
            url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
            
            # Get current timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Prepare payload
            payload = {
                "form_type": form_type,
                "form_data": form_data,
                "validated": True,
                "validation_timestamp": timestamp,
                "validator": "Form Validation System"
            }
            
            # Add comparison info if available
            if comparison_result:
                payload["comparison"] = {
                    "matches": comparison_result.get("matches", False),
                    "timestamp": timestamp
                }
            
            # Make the API call
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_API_KEY"  # Replace with actual auth if needed
            }
            
            # For testing we can mock the response
            # Uncomment below for actual API call
            # response = requests.post(url, json=payload, headers=headers)
            
            # Mock response for development (remove in production)
            mock_response = {
                "success": True,
                "message": f"Successfully updated {form_type} in database",
                "transaction_id": "txn_" + timestamp.replace(":", "").replace(".", ""),
                "updated_fields": list(form_data.keys())
            }
            
            # Return success result (using mock for now)
            return {
                "success": True,
                "message": f"Successfully updated {form_type} in database",
                "details": mock_response
                # In production:
                # "details": response.json() if response.content else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating database: {str(e)}",
                "details": {"exception": str(e)}
            }