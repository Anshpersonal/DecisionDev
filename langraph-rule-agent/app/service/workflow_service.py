# app/service/workflow_service.py - Service for workflow orchestration using LangGraph

from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain.globals import set_tracing_callback_enabled
import json

# # Enable tracing for LangSmith
# set_tracing_callback_enabled(True)

class GraphState(TypedDict, total=False):
    """Type definition for graph state"""
    user_input: str
    use_decision_engine: bool
    rule_validation_needed: bool
    form_type: str
    file_path: str
    extracted_data: Dict[str, Any]
    validation_result: Dict[str, Any]
    error: str
    final_response: str

class WorkflowService:
    """Service for orchestrating workflows using LangGraph"""
    
    def __init__(self, llm, rag_service, ocr_service):
        """
        Initialize workflow service
        
        Args:
            llm: LLM model for the workflow
            rag_service: RAG service for document Q&A
            ocr_service: OCR service for data extraction
        """
        self.llm = llm
        self.rag_service = rag_service
        self.ocr_service = ocr_service
        self.workflow = self._create_workflow()
    
    def _tool_selector(self, state: GraphState) -> GraphState:
        """
        Root node that decides whether to use LLM directly or go through rule validation
        
        Args:
            state: Current state
            
        Returns:
            Updated state with decision
        """
        if "error" in state:
            return state
        
        # If use_decision_engine is False, skip rule validation
        if not state.get("use_decision_engine", False):
            return state
        
        user_input = state["user_input"]
        
        # Prompt to decide if rule validation is needed
        prompt = ChatPromptTemplate.from_template("""
        You are an assistant that helps decide whether a user query requires form validation.
        
        User query: {user_input}
        
        Does this query appear to be asking about validating or processing a form, document, 
        or extracting data from a file? Answer with 'yes' or 'no'.
        """)
        
        try:
            # Invoke the LLM to make the decision
            response = self.llm.invoke(prompt.format_messages(user_input=user_input))
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Check if the response indicates rule validation is needed
            rule_validation_needed = "yes" in content.lower()
            
            # Detect potential form type
            form_type = "generic"
            if "renewal" in user_input.lower():
                form_type = "renewals"
            elif "withdrawal" in user_input.lower():
                form_type = "withdrawals"
            
            return {
                **state, 
                "rule_validation_needed": rule_validation_needed,
                "form_type": form_type
            }
        except Exception as e:
            return {**state, "error": f"Error in tool selection: {str(e)}"}
    
    def _rule_validation_entry(self, state: GraphState) -> GraphState:
        """
        Entry point for rule validation workflow
        
        Args:
            state: Current state
            
        Returns:
            Updated state prepared for rule validation
        """
        if "error" in state:
            return state
        
        # Extract potential file path from user input (simplified)
        user_input = state["user_input"]
        
        # Simple file path extraction - in a real implementation this would be more sophisticated
        import re
        file_path_match = re.search(r'file[:\s]+([^\s,\.]+)', user_input)
        file_path = file_path_match.group(1) if file_path_match else "test_form.pdf"
        
        return {**state, "file_path": file_path}
    
    def _ocr_node(self, state: GraphState) -> GraphState:
        """
        Extract data using OCR
        
        Args:
            state: Current state
            
        Returns:
            Updated state with extracted data
        """
        if "error" in state:
            return state
        
        file_path = state.get("file_path", "test_form.pdf")
        form_type = state.get("form_type", "generic")
        
        try:
            # If this is a test run or we don't have a file path, use test data
            if file_path == "test_form.pdf":
                extracted_data = self.ocr_service.extract_test_data(form_type)
            else:
                extracted_data = self.ocr_service.extract_form_data(file_path)
            
            if "error" in extracted_data:
                return {**state, "error": extracted_data["error"]}
            
            return {**state, "extracted_data": extracted_data}
        except Exception as e:
            return {**state, "error": f"Error in OCR processing: {str(e)}"}
    
    def _llm_response(self, state: GraphState) -> GraphState:
        """
        Generate a response using either extracted data or RAG
        
        Args:
            state: Current state
            
        Returns:
            Updated state with final response
        """
        if "error" in state:
            return {**state, "final_response": f"I apologize, but I encountered an error: {state['error']}"}
        
        user_input = state["user_input"]
        
        # If we have extracted data, format a response that includes it
        if "extracted_data" in state:
            extracted_data = state["extracted_data"]
            
            # Create a prompt that includes the extracted data
            prompt = ChatPromptTemplate.from_template("""
            You are an assistant that helps users understand extracted form data.
            
            User query: {user_input}
            
            Extracted data: {extracted_data}
            
            Please provide a helpful response that explains the extracted data in natural language.
            Focus on the most important fields and provide a concise summary.
            """)
            
            try:
                response = self.llm.invoke(prompt.format_messages(
                    user_input=user_input,
                    extracted_data=json.dumps(extracted_data, indent=2)
                ))
                
                content = response.content if hasattr(response, 'content') else str(response)
                return {**state, "final_response": content}
            except Exception as e:
                print(f"Error formatting extracted data: {e}")
                # Fall back to simpler response
                return {**state, "final_response": f"I've analyzed the form and extracted the following data: {json.dumps(extracted_data, indent=2)}"}
        
     
  
            # Fall back to direct LLM response
        try:
            response = self.llm.invoke(user_input)
            content = response.content if hasattr(response, 'content') else str(response)
            return {**state, "final_response": content}
        except Exception as inner_e:
            return {**state, "final_response": f"I apologize, but I couldn't process your request: {str(inner_e)}"}
    
    def _router(self, state: GraphState) -> str:
        """
        Route to the next node based on state
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state:
            return "llm_response"
        
        if state.get("rule_validation_needed", False):
            return "rule_validation_entry"
        else:
            return "llm_response"
    
    def _rule_validation_router(self, state: GraphState) -> str:
        """
        Route within the rule validation workflow
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state:
            return "llm_response"
        
        # For now, always go to OCR node
        return "ocr_node"
    
    def _post_ocr_router(self, state: GraphState) -> str:
        """
        Route after OCR processing
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state:
            return "llm_response"
        
        # For now, we'll just go to LLM response after OCR
        # In the future, this would go to a rule validation node
        return "llm_response"
    
    def _create_workflow(self):
        """
        Create the LangGraph workflow
        
        Returns:
            StateGraph: Compiled workflow
        """
        # Create the StateGraph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("tool_selector", self._tool_selector)
        workflow.add_node("rule_validation_entry", self._rule_validation_entry)
        workflow.add_node("ocr_node", self._ocr_node)
        workflow.add_node("llm_response", self._llm_response)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "tool_selector",
            self._router,
            {
                "rule_validation_entry": "rule_validation_entry",
                "llm_response": "llm_response"
            }
        )
        
        workflow.add_conditional_edges(
            "rule_validation_entry",
            self._rule_validation_router,
            {
                "ocr_node": "ocr_node"
            }
        )
        
        workflow.add_conditional_edges(
            "ocr_node",
            self._post_ocr_router,
            {
                "llm_response": "llm_response"
            }
        )
        
        # Set entry point
        workflow.set_entry_point("tool_selector")
        
        # Compile the graph
        return workflow.compile()
    
    def process_message(self, user_input, use_decision_engine=False):
        """
        Process a user message through the workflow
        
        Args:
            user_input (str): User input text
            use_decision_engine (bool): Whether to consider using rule validation
            
        Returns:
            dict: Result of the workflow
        """
        initial_state = {
            "user_input": user_input,
            "use_decision_engine": use_decision_engine
        }
        
        try:
            # Invoke the workflow
            result = self.workflow.invoke(initial_state)
            
            # Return the final response
            return {
                "input": user_input,
                "output": result.get("final_response", "Sorry, I couldn't process your request.")
            }
        except Exception as e:
            print(f"Error in workflow: {e}")
            return {
                "input": user_input,
                "output": f"I apologize, but I encountered an error while processing your request. Please try again.",
                "error": str(e)
            }