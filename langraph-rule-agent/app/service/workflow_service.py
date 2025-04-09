# app/service/workflow_service.py - Service for workflow orchestration using LangGraph

from typing import Dict, Any, TypedDict, Annotated, Sequence, Union, List
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.globals import set_tracing_callback_enabled
import re
import json
from pydantic import BaseModel
from app.model.rule_model import Tool

# Enable tracing for LangSmith
set_tracing_callback_enabled(True)

class GraphState(TypedDict, total=False):
    """Type definition for graph state"""
    user_input: str
    use_decision_engine: bool
    available_tools: List[Tool]
    selected_tool: Tool
    tool_args: Dict[str, Any]
    tool_result: Any
    rag_result: str
    error: str
    final_response: str
    
class ToolSelection(BaseModel):
    """Model for tool selection output"""
    tool_name: str
    reason: str
    
class ToolArguments(BaseModel):
    """Model for tool arguments"""
    arguments: Dict[str, Any]
    
class WorkflowService:
    """Service for orchestrating workflows using LangGraph"""
    
    def __init__(self, llm, rag_service, decision_services, tools):
        """
        Initialize workflow service
        
        Args:
            llm: LLM model for the workflow
            rag_service: RAG service for document Q&A
            decision_services: Dictionary of decision services
            tools: List of available tools
        """
        self.llm = llm
        self.rag_service = rag_service
        self.decision_services = decision_services
        self.tools = tools
        self.workflow = self._create_workflow()
        
    def _tool_selector(self, state: GraphState) -> GraphState:
        """
        Select a tool based on user input
        
        Args:
            state: Current state
            
        Returns:
            Updated state with selected tool
        """
        if "error" in state:
            return state
        
        if not state.get("use_decision_engine", False):
            # Skip tool selection if not using decision engine
            return state
        
        user_input = state["user_input"]
        available_tools = state["available_tools"]
        
        if not available_tools:
            return {**state, "error": "No tools available"}
        
        # Create a prompt for tool selection
        tool_descriptions = "\n".join([
            f"- {tool.toolName}: {tool.toolDescription}" 
            for tool in available_tools
        ])
        
        prompt = ChatPromptTemplate.from_template("""
        You are an assistant that helps select the most appropriate tool for a user query.
        
        Available tools:
        {tool_descriptions}
        
        User query: {user_input}
        
        Based on the user query, select the most appropriate tool. If no tool is appropriate, respond with "none".
        Return your response as a JSON with the following structure:
        {{"tool_name": "name of the tool or 'none'", "reason": "brief explanation for your choice"}}
        """)
        
        # Parse the response as JSON
        json_parser = JsonOutputParser(pydantic_object=ToolSelection)
        tool_selection_chain = prompt | self.llm | json_parser
        
        try:
            # Invoke the chain
            selection_result = tool_selection_chain.invoke({
                "tool_descriptions": tool_descriptions,
                "user_input": user_input
            })
            
            if selection_result.tool_name.lower() == "none":
                # No appropriate tool found
                return state
            
            # Find the selected tool
            selected_tool = next(
                (tool for tool in available_tools if tool.toolName == selection_result.tool_name), 
                None
            )
            
            if selected_tool:
                return {**state, "selected_tool": selected_tool}
            else:
                return state  # No tool was selected
            
        except Exception as e:
            print(f"Error in tool selection: {e}")
            return state  # Continue without a tool
    
    def _argument_extractor(self, state: GraphState) -> GraphState:
        """
        Extract arguments for the selected tool
        
        Args:
            state: Current state
            
        Returns:
            Updated state with tool arguments
        """
        if "error" in state or "selected_tool" not in state:
            return state
        
        user_input = state["user_input"]
        selected_tool = state["selected_tool"]
        
        # Create a prompt for argument extraction
        args_info = "\n".join([
            f"- {arg['argName']}: {arg['argDescription']}" 
            for arg in selected_tool.args
        ])
        
        prompt = ChatPromptTemplate.from_template("""
        You are an assistant that extracts arguments for a tool from user input.
        
        Tool: {tool_name}
        Tool description: {tool_description}
        
        Required arguments:
        {args_info}
        
        User input: {user_input}
        
        Extract the values for the required arguments from the user input.
        Return your response as a JSON with the following structure:
        {{"arguments": {{"arg1": "value1", "arg2": "value2", ...}}}}
        
        If you can't find a value for an argument, use a reasonable default or leave it empty.
        """)
        
        # Parse the response as JSON
        json_parser = JsonOutputParser(pydantic_object=ToolArguments)
        arg_extraction_chain = prompt | self.llm | json_parser
        
        try:
            # Invoke the chain
            extraction_result = arg_extraction_chain.invoke({
                "tool_name": selected_tool.toolName,
                "tool_description": selected_tool.toolDescription,
                "args_info": args_info,
                "user_input": user_input
            })
            
            return {**state, "tool_args": extraction_result.arguments}
            
        except Exception as e:
            print(f"Error in argument extraction: {e}")
            return {**state, "error": f"Failed to extract arguments: {str(e)}"}
    
    def _execute_tool(self, state: GraphState) -> GraphState:
        """
        Execute the selected tool with the extracted arguments
        
        Args:
            state: Current state
            
        Returns:
            Updated state with tool result
        """
        if "error" in state:
            return state
        
        if "selected_tool" not in state or "tool_args" not in state:
            return state
        
        selected_tool = state["selected_tool"]
        tool_args = state["tool_args"]
        
        # Get the appropriate decision service
        service_type = selected_tool.engine
        if service_type not in self.decision_services:
            return {**state, "error": f"Decision service not available: {service_type}"}
        
        service = self.decision_services[service_type]
        
        try:
            # Invoke the decision service
            result = service.invoke_decision_service(selected_tool.toolPath, tool_args)
            
            if "error" in result:
                return {**state, "error": result["error"]}
            
            # Extract the output property
            output_property = selected_tool.output
            if output_property in result:
                return {**state, "tool_result": result[output_property]}
            else:
                return {**state, "error": f"Output property not found: {output_property}"}
                
        except Exception as e:
            return {**state, "error": f"Error executing tool: {str(e)}"}
    
    def _process_with_rag(self, state: GraphState) -> GraphState:
        """
        Process the user input with RAG if no tool was used
        
        Args:
            state: Current state
            
        Returns:
            Updated state with RAG result
        """
        if "error" in state or "tool_result" in state:
            return state
        
        user_input = state["user_input"]
        
        try:
            rag_result = self.rag_service.process_query(user_input)
            return {**state, "rag_result": rag_result}
        except Exception as e:
            return {**state, "error": f"Error in RAG processing: {str(e)}"}
    
    def _generate_response(self, state: GraphState) -> GraphState:
        """
        Generate the final response based on tool result or RAG result
        
        Args:
            state: Current state
            
        Returns:
            Updated state with final response
        """
        if "error" in state:
            return {**state, "final_response": f"I apologize, but I encountered an error: {state['error']}"}
        
        user_input = state["user_input"]
        
        # If tool was used, format the tool result
        if "tool_result" in state:
            tool_result = state["tool_result"]
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant that provides natural language responses based on system results.
            
            User asked: {user_input}
            
            System result: {tool_result}
            
            Please provide a natural, conversational response that incorporates the system result.
            Make it sound like you're having a conversation, not just returning data.
            """)
            
            try:
                response = prompt.invoke({
                    "user_input": user_input,
                    "tool_result": tool_result
                }).content
                
                return {**state, "final_response": response}
            except Exception as e:
                print(f"Error formatting tool result: {e}")
                return {**state, "final_response": str(tool_result)}
        
        # If RAG was used, use the RAG result
        elif "rag_result" in state:
            return {**state, "final_response": state["rag_result"]}
        
        # Fallback response
        else:
            return {**state, "final_response": "I'm sorry, but I couldn't find an answer to your question."}
    
    def _router(self, state: GraphState) -> str:
        """
        Route to the next node in the workflow
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state:
            return "generate_response"
        
        if state.get("use_decision_engine", False) and "selected_tool" in state:
            return "extract_arguments"
        else:
            return "process_with_rag"
    
    def _post_argument_router(self, state: GraphState) -> str:
        """
        Route after argument extraction
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state:
            return "generate_response"
        
        if "tool_args" in state:
            return "execute_tool"
        else:
            return "process_with_rag"
    
    def _post_execution_router(self, state: GraphState) -> str:
        """
        Route after tool execution
        
        Args:
            state: Current state
            
        Returns:
            Name of the next node
        """
        if "error" in state or "tool_result" in state:
            return "generate_response"
        else:
            return "process_with_rag"
    
    def _create_workflow(self):
        """
        Create the LangGraph workflow
        
        Returns:
            StateGraph: Compiled workflow
        """
        # Create the StateGraph with the state type
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("tool_selector", self._tool_selector)
        workflow.add_node("extract_arguments", self._argument_extractor)
        workflow.add_node("execute_tool", self._execute_tool)
        workflow.add_node("process_with_rag", self._process_with_rag)
        workflow.add_node("generate_response", self._generate_response)
        
        # Add conditional edgesz
        workflow.add_conditional_edges(
            "tool_selector",
            self._router,
            {
                "extract_arguments": "extract_arguments",
                "process_with_rag": "process_with_rag"
            }
        )
        
        workflow.add_conditional_edges(
            "extract_arguments",
            self._post_argument_router,
            {
                "execute_tool": "execute_tool",
                "process_with_rag": "process_with_rag"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_tool",
            self._post_execution_router,
            {
                "generate_response": "generate_response",
                "process_with_rag": "process_with_rag"
            }
        )
        
        # Add remaining edges
        workflow.add_edge("process_with_rag", "generate_response")
        
        # Set entry point
        workflow.set_entry_point("tool_selector")
        
        # Compile the graph
        return workflow.compile()
    
    def process_message(self, user_input, use_decision_engine=False):
        """
        Process a user message through the workflow
        
        Args:
            user_input (str): User input text
            use_decision_engine (bool): Whether to use the decision engine
            
        Returns:
            dict: Result of the workflow
        """
        initial_state = {
            "user_input": user_input,
            "use_decision_engine": use_decision_engine,
            "available_tools": self.tools if use_decision_engine else []
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