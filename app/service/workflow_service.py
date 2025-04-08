# app/services/workflow_service.py - LangGraph workflow implementation

from typing import Dict, Any, TypedDict, Annotated, Sequence, Union
from langgraph.graph import StateGraph
from app.service.ocr_service import OCRService
from app.service.validation_service import ValidationService
from app.model.rule_model import ValidationResult

class GraphState(TypedDict, total=False):
    """Type definition for graph state"""
    form_data: dict
    form_type: str
    is_test: bool
    vector_db: any
    json_data: dict
    rules: list
    validation_result: dict
    error: str
    response: str
    validation_details: dict
    db_data: dict  # Data from database API
    comparison_result: dict  # Result of comparing OCR with DB data
    update_result: dict  # Result of database update operation

class WorkflowService:
    """Service for managing the LangGraph workflow"""
    
    def __init__(self, ocr_service, validation_service, api_service=None, comparison_service=None, update_service=None, llm_model=None):
        """
        Initialize workflow service
        
        Args:
            ocr_service: OCR service for data extraction
            validation_service: Validation service for form validation
            api_service: API service for database queries
            comparison_service: Service for comparing OCR and DB data
            update_service: Service for updating external database
            llm_model: LLM model for comparison (if comparison_service not provided)
        """
        self.ocr_service = ocr_service
        self.validation_service = validation_service
        self.api_service = api_service
        self.comparison_service = comparison_service
        self.update_service = update_service
        self.llm_model = llm_model
        self.workflow = self._create_workflow()
    
    def _input_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Initial state to process form inputs."""
        print(inputs)
        return {
            "form_data": inputs["form_data"],
            "form_type": inputs["form_type"],
            "vector_db": inputs.get("vector_db"),
            "is_test": inputs.get("is_test", False)
        }

    def _ocr_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from form using OCR API."""
        
        try:
            # Call OCR API or use test data if testing
            if inputs.get("is_test", False):
                # Simulated data for testing
                json_data = self.ocr_service.extract_test_data(inputs["form_type"])
            else:
                # Extract actual form data
                json_data = self.ocr_service.extract_form_data(inputs["form_data"]["path"])
            
            if "error" in json_data:
                return {"error": json_data["error"]}
            
            return {
                "json_data": json_data,
                "form_type": inputs["form_type"],
                "vector_db": inputs["vector_db"]
            }
        
        except Exception as e:
            return {"error": f"OCR processing error: {str(e)}"}

    def _rule_retrieval_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve validation rules from vector DB."""
        try:
            if "error" in inputs:
                return inputs  # Pass through errors
            
            form_type = inputs["form_type"]
            vector_db = inputs["vector_db"]
            
            # Retrieve rules from vector DB
            rules = vector_db.retrieve_validation_rules(form_type)
            
            return {
                "rules": rules,
                "json_data": inputs["json_data"],
                "form_type": form_type
            }
        
        except Exception as e:
            return {"error": f"Rule retrieval error: {str(e)}"}

    def _validation_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON data against rules using LLM."""
        try:
            if "error" in inputs:
                return inputs  # Pass through errors
            
            json_data = inputs["json_data"]
            rules = inputs["rules"]
            form_type = inputs["form_type"]
            
            # Validate using the validation service
            validation_result = self.validation_service.validate_form_data(
                json_data, rules, form_type
            )
            
            return {
                "validation_result": validation_result.to_dict(),
                "json_data": json_data,
                "form_type": form_type
            }
        
        except Exception as e:
            return {"error": f"Validation error: {str(e)}"}
            
    def _api_fetch_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from the database API if validation passed."""
        try:
            if "error" in inputs:
                return inputs  # Pass through errors
                
            # Check if validation passed
            validation_result = inputs["validation_result"]
            if not validation_result.get("valid", False):
                # If validation failed, skip this step
                return {
                    "validation_result": validation_result,
                    "json_data": inputs["json_data"],
                    "form_type": inputs["form_type"]
                }
            
            # Validation passed, fetch data from API
            json_data = inputs["json_data"]
            form_type = inputs["form_type"]
            
            # Get the appropriate ID field based on form type
            id_field = "contractNumber" if form_type == "renewals" else "withdrawals"
            
            # Get ID from OCR data
            form_id = json_data.get(id_field)
            if not form_id:
                return {
                    "error": f"Could not find {id_field} in extracted data",
                    "json_data": json_data,
                    "form_type": form_type,
                    "validation_result": validation_result
                }
            
            # Call the appropriate API method based on form type
            db_data = self.api_service.fetch_data_by_form_type(form_type, form_id)
            
            # Check for errors in API response
            if "error" in db_data:
                return {
                    "error": db_data["error"],
                    "json_data": json_data,
                    "form_type": form_type,
                    "validation_result": validation_result
                }
            
            # Return API data for comparison
            return {
                "db_data": db_data,
                "json_data": json_data,
                "form_type": form_type,
                "validation_result": validation_result
            }
        
        except Exception as e:
            return {"error": f"API fetch error: {str(e)}"}

    def _comparison_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Compare OCR-extracted data with database data using LLM."""
        try:
            if "error" in inputs:
                return inputs  # Pass through errors
            
            # If no DB data, skip comparison
            if "db_data" not in inputs:
                return {
                    "validation_result": inputs["validation_result"],
                    "json_data": inputs["json_data"],
                    "form_type": inputs["form_type"]
                }
            
            json_data = inputs["json_data"]
            db_data = inputs["db_data"]
            form_type = inputs["form_type"]
            validation_result = inputs["validation_result"]
            
            # Compare OCR data with DB data
            comparison_result = self.comparison_service.compare_data(
                json_data, db_data, form_type
            )
            
            return {
                "validation_result": validation_result,
                "json_data": json_data,
                "form_type": form_type,
                "db_data": db_data,
                "comparison_result": comparison_result
            }
        
        except Exception as e:
            return {"error": f"Comparison error: {str(e)}"}
    
    def _update_database_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Update external database with validated form data."""
        try:
            if "error" in inputs:
                return inputs  # Pass through errors
            
            # Skip update if validation failed or comparison failed
            validation_result = inputs["validation_result"]
            if not validation_result.get("valid", False):
                return inputs  # Skip update, return current state
            
            # Check if comparison was done and if it passed
            if "comparison_result" in inputs:
                comparison_result = inputs["comparison_result"]
                if not comparison_result.get("matches", False):
                    # Comparison failed, don't update database
                    return {
                        **inputs,
                        "update_result": {
                            "success": False,
                            "message": "Database update skipped due to data discrepancies",
                            "details": {"reason": "comparison_failed"}
                        }
                    }
            
            # Proceed with database update
            json_data = inputs["json_data"]
            form_type = inputs["form_type"]
            comparison_result = inputs.get("comparison_result")
            
            # Call update service
            update_result = self.update_service.update_database(
                form_type, 
                json_data, 
                validation_result,
                comparison_result
            )
            
            # Return current state with update result
            return {
                **inputs,
                "update_result": update_result
            }
        
        except Exception as e:
            # Return error but preserve other state
            return {
                **inputs,
                "update_result": {
                    "success": False,
                    "message": f"Error updating database: {str(e)}",
                    "details": {"exception": str(e)}
                }
            }

    def _response_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user-friendly response based on validation, comparison, and update results."""
        try:
            if "error" in inputs:
                return {"response": f"⚠️ Error in processing: {inputs['error']}"}
            
            validation_result = ValidationResult.from_dict(inputs["validation_result"])
            form_type = inputs["form_type"]
            
            # Format the validation response
            response = validation_result.get_formatted_response(form_type)
            
            # Add comparison results to the response if available
            if "comparison_result" in inputs and "db_data" in inputs:
                comparison_result = inputs["comparison_result"]
                
                if comparison_result.get("matches", False):
                    comparison_message = "\n\n✅ The form data matches the database records."
                else:
                    comparison_message = "\n\n⚠️ The following discrepancies were found between the form and database records:"
                    for result in comparison_result.get("comparison_results", []):
                        if not result.get("match", False):
                            comparison_message += f"\n- {result.get('field')}: Form has '{result.get('ocr_value')}', Database has '{result.get('db_value')}'"
                
                response = response + comparison_message
            
            # Add database update results if available
            if "update_result" in inputs:
                update_result = inputs["update_result"]
                if update_result.get("success", False):
                    update_message = f"\n\n✅ Database successfully updated with validated form data."
                    if "transaction_id" in update_result.get("details", {}):
                        update_message += f"\nTransaction ID: {update_result['details']['transaction_id']}"
                else:
                    update_message = f"\n\n❌ Database update failed: {update_result.get('message', 'Unknown error')}"
                
                response = response + update_message
            
            result = {
                "response": response,
                "validation_details": inputs["validation_result"],
                "json_data": inputs["json_data"],
                "form_type": form_type
            }
            
            # Add additional result data if available
            if "db_data" in inputs:
                result["db_data"] = inputs["db_data"]
            
            if "comparison_result" in inputs:
                result["comparison_result"] = inputs["comparison_result"]
                
            if "update_result" in inputs:
                result["update_result"] = inputs["update_result"]
            
            return result
        
        except Exception as e:
            return {"response": f"⚠️ Error generating response: {str(e)}"}

    def _handle_ocr_error(self, state):
        """Conditional edge handler for OCR errors"""
        if "error" in state:
            return "response_node"
        return "rule_retrieval_node"
    
    def _handle_rule_error(self, state):
        """Conditional edge handler for rule retrieval errors"""
        if "error" in state:
            return "response_node"
        return "validation_node"

    def _handle_validation_result(self, state):
        """Conditional edge handler for validation results"""
        # If there's an error or validation failed, skip API fetch
        if "error" in state or not state.get("validation_result", {}).get("valid", False):
            return "response_node"
        return "api_fetch_node"
        
    def _create_workflow(self):
        """Create and compile the LangGraph workflow."""
        # Create the StateGraph with the state type
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("input_node", self._input_state)
        workflow.add_node("ocr_node", self._ocr_state)
        workflow.add_node("rule_retrieval_node", self._rule_retrieval_state)
        workflow.add_node("validation_node", self._validation_state)
        workflow.add_node("api_fetch_node", self._api_fetch_state)
        workflow.add_node("comparison_node", self._comparison_state)
        workflow.add_node("update_database_node", self._update_database_state)
        workflow.add_node("response_node", self._response_state)
        
        # Add edges with conditional handling
        workflow.add_edge("input_node", "ocr_node")
        workflow.add_conditional_edges(
            "ocr_node",
            self._handle_ocr_error,
            {
                "rule_retrieval_node": "rule_retrieval_node",
                "response_node": "response_node"
            }
        )
        workflow.add_conditional_edges(
            "rule_retrieval_node",
            self._handle_rule_error,
            {
                "validation_node": "validation_node",
                "response_node": "response_node"
            }
        )
        # Add conditional edge after validation based on result
        workflow.add_conditional_edges(
            "validation_node",
            self._handle_validation_result,
            {
                "api_fetch_node": "api_fetch_node",
                "response_node": "response_node"
            }
        )
        workflow.add_edge("api_fetch_node", "comparison_node")
        workflow.add_edge("comparison_node", "update_database_node")  # Add database update step
        workflow.add_edge("update_database_node", "response_node")
        
        # Set entry point
        workflow.set_entry_point("input_node")
        
        # Compile the graph
        return workflow.compile()
    
    def run_workflow(self, form_data, form_type, vector_db, is_test):
        """
        Run the form validation workflow
        
        Args:
            form_data: Form data dictionary with path
            form_type: Type of form
            vector_db: Vector database instance
            is_test: Whether this is a test run
            
        Returns:
            dict: Results of the workflow
        """
        print("executing run workflow")
        print(is_test)
        inputs = {
            "form_data": form_data,
            "form_type": form_type,
            "vector_db": vector_db,
            "is_test": is_test
        }

        
        try:
            # Invoke the workflow
            result = self.workflow.invoke(inputs)
            return result
        except Exception as e:
            return {
                "error": f"Workflow error: {str(e)}",
                "response": f"⚠️ Error running validation workflow: {str(e)}"
            }