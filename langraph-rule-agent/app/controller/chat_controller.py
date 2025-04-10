# app/controller/chat_controller.py - Controller for chat requests

from flask import Blueprint, request, jsonify
from app.service.llm_service import LLMService
from app.service.workflow_service import WorkflowService
from app.service.rag_service import RAGService
from app.service.ocr_service import OCRService
import os
from langsmith import Client
from app.config import Config

config = Config()

chat_bp = Blueprint('chat', __name__)

# Initialize services
llm_service = LLMService()
llm = llm_service.get_llm()
rag_service = RAGService(llm)
ocr_service = OCRService(config.OCR_API_ENDPOINT)
workflow_service = WorkflowService(llm, rag_service, ocr_service)

# Initialize LangSmith client if API key is available


        
langsmith_client = Client()


# Initialize the RAG service with documents
def initialize_rag():
    """Initialize the RAG service with documents from catalogs"""
    
    # Find catalog directories
    catalog_dirs = []
    for root, dirs, files in os.walk(config.DATADIR):
        for dir_name in dirs:
            if dir_name == 'catalog':
                catalog_dirs.append(os.path.join(root, dir_name))
    
    # Ingest documents from catalog directories
    total_docs = 0
    for directory in catalog_dirs:
        if os.path.exists(directory):
            docs_ingested = rag_service.ingest_documents_from_directory(directory)
            total_docs += docs_ingested
            print(f"Ingested {docs_ingested} documents from {directory}")
    
    print(f"Initialized RAG service with {total_docs} documents from {len(catalog_dirs)} catalog directories")

# Initialize the RAG service
initialize_rag()

@chat_bp.route('/chat_with_tools', methods=['GET'])
def chat_with_tools():
    """Handle chat with decision tools"""
    if request.method == 'GET':
        user_input = request.args.get('userMessage', '')
        conversation_id = request.args.get('conversationId', '')
        
        if not user_input:
            return jsonify({
                "input": "",
                "output": "Please provide a message",
                "type": "error"
            })
        
        # Process the message with decision engine, passing conversation ID
        result = workflow_service.process_message(
            user_input, 
            use_decision_engine=True,
            conversation_id=conversation_id
        )
        
        return jsonify(result)

@chat_bp.route('/chat_without_tools', methods=['GET'])
def chat_without_tools():
    """Handle chat without decision tools (RAG only)"""
    if request.method == 'GET':
        user_input = request.args.get('userMessage', '')
        conversation_id = request.args.get('conversationId', '')
        
        if not user_input:
            return jsonify({
                "input": "",
                "output": "Please provide a message",
                "type": "error"
            })
        
        # Process the message without decision engine, passing conversation ID
        result = workflow_service.process_message(
            user_input, 
            use_decision_engine=False,
            conversation_id=conversation_id
        )
        
        return jsonify(result)
    

@chat_bp.route('/start_conversation', methods=['GET'])
def start_conversation():
    """Start a new conversation and return a conversation ID"""
    import uuid
    conversation_id = str(uuid.uuid4())
    
    return jsonify({
        "conversation_id": conversation_id,
        "message": "Conversation started",
        "status": "success"
    })

@chat_bp.route('/inspect_memory', methods=['GET'])
def inspect_memory():
    """Inspect the memory for a specific conversation"""
    conversation_id = request.args.get('conversationId', '')
    
    if not conversation_id:
        return jsonify({
            "status": "error",
            "message": "Conversation ID is required"
        }), 400
    
    if conversation_id not in workflow_service.conversations:
        return jsonify({
            "status": "error",
            "message": f"No memory found for conversation ID: {conversation_id}",
            "available_conversations": list(workflow_service.conversations.keys())
        }), 404
    
    # Get the memory
    memory = workflow_service.conversations[conversation_id]
    memory_vars = memory.load_memory_variables({})
    
    return jsonify({
        "status": "success",
        "conversation_id": conversation_id,
        "memory": memory_vars,
        "memory_size": len(str(memory_vars.get("history", "")))
    })

@chat_bp.route('/reset_memory', methods=['POST'])
def reset_memory():
    """Reset the memory for a specific conversation"""
    conversation_id = request.args.get('conversationId', '')
    
    if not conversation_id:
        return jsonify({
            "status": "error",
            "message": "Conversation ID is required"
        }), 400
    
    # Remove the conversation from memory if it exists
    if conversation_id in workflow_service.conversations:
        del workflow_service.conversations[conversation_id]
        
    # Create a new memory for this conversation
    workflow_service.get_or_create_memory(conversation_id)
    
    return jsonify({
        "status": "success",
        "message": f"Memory reset for conversation: {conversation_id}"
    })  

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "llm": llm_service.llm.__class__.__name__ if llm_service.llm else "Not initialized",
        "rag_initialized": rag_service.chain is not None if hasattr(rag_service, 'chain') else False,
        "langsmith_configured": langsmith_client is not None
    }
    return jsonify(status)