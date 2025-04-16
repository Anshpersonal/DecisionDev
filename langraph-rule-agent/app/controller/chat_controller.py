# app/controller/chat_controller.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import uuid
import json
from datetime import datetime
import boto3
from confluent_kafka import Producer, Consumer
from app.service.llm_service import LLMService
from app.service.workflow_service import WorkflowService
from app.service.rag_service import RAGService
from app.service.ocr_service import OCRService
import os
from langsmith import Client
from app.config import Config
from app.service.test_service import TestService

# Initialize Config and Blueprint
config = Config()
chat_bp = Blueprint('chat', __name__)

# Initialize LLM, RAG, OCR, and Workflow services
llm_service = LLMService()
llm = llm_service.get_llm()
rag_service = RAGService(llm)
ocr_service = OCRService(config.OCR_API_ENDPOINT)
workflow_service = WorkflowService(llm, rag_service, ocr_service)
test_service =TestService(rag_service)

# Initialize LangSmith client (if configured)
langsmith_client = Client()

# ----------------------------
# S3 and Kafka Client Setup
# ----------------------------
S3_BUCKET = config.S3_BUCKET
s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region_name=config.region_name
)

producer_config = {
    "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": config.KAFKA_API_KEY,
    "sasl.password": config.KAFKA_API_SECRET
}
consumer_config = {
    "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": config.KAFKA_API_KEY,
    "sasl.password": config.KAFKA_API_SECRET,
    "group.id": config.KAFKA_CONSUMER_GROUP_ID,
    "auto.offset.reset": "earliest"
}
producer = Producer(producer_config)

# Alias mapping for OCR result transformation
alias_mapping = {
    "contract-number": "contractNumber",
    "owner-signature-date": "ownerSignatureDate",
    "subsequent-guarantee-period": "guaranteePeriod",
    "owner-name": "ownerName",
    "owner-email-address": "emailAddress",
    "owner-phone-number": "phoneNumber"
}

# ----------------------------
# Helper Functions
# ----------------------------
def uploadFileinS3(file, file_name):
    try:
        s3_client.upload_fileobj(file, S3_BUCKET, file_name)
        return "File uploaded successfully"
    except Exception as e:
        return {"error": str(e)}

def generate_message(file_path, query_file, tracking_id):
    data = {
        "id": str(uuid.uuid4()),
        "correlationid": str(uuid.uuid4()),
        "source": "mass.zinnovate",
        "carrier": "MASS",
        "specversion": "V1",
        "type": "EXTRACTION",
        "datacontenttype": "application/json",
        "time": datetime.utcnow().isoformat(),
        "data": json.dumps({
            "file": file_path,
            "queryFile": query_file
        }),
        "identifier": [{"trackingId": tracking_id}]
    }
    return json.dumps(data, indent=4)

def send_message(message, tracking_id):
    producer.produce(config.KAFKA_TOPIC, key=tracking_id, value=message)
    producer.flush()

def consume_messages(topic, timeout, tracking_id):
    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])
    try:
        while True:
            msg = consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            value = json.loads(msg.value().decode())
            # The 'data' field is a JSON string; decode to a dict:
            message_obj = json.loads(value["data"])
            if value["identifier"][0]["trackingId"] == tracking_id:
                consumer.close()
                return message_obj
    except KeyboardInterrupt:
        print("Consumer interrupted")
    finally:
        consumer.close()
    return {}

def transform_ocr_result(ocr_result):
    transformed_data = {}
    for item in ocr_result.get("extractionResults", []):
        alias = item.get("queryAlias")
        if alias in alias_mapping and item.get("queryResults"):
            transformed_data[alias_mapping[alias]] = item["queryResults"][0].get("queryAnswer", "")
    return transformed_data


@chat_bp.route('/rule_val',methods=['GET'])
def rule_val():
    if request.method=='GET':
        # user_input = request.args.get('rule','')
        result = test_service.test_all_rules()
        return jsonify(result)
    return

# ----------------------------
# Existing Chat Endpoints
# ----------------------------
@chat_bp.route('/chat_with_tools', methods=['GET'])
def chat_with_tools():
    """Handle chat with decision tools."""
    user_input = request.args.get('userMessage', '')
    conversation_id = request.args.get('conversationId', '')
    if not user_input:
        return jsonify({"input": "", "output": "Please provide a message", "type": "error"})
    
    result = workflow_service.process_message(
        user_input, 
        use_decision_engine=True,
        conversation_id=conversation_id
    )
    return jsonify(result)

@chat_bp.route('/chat_without_tools', methods=['GET'])
def chat_without_tools():
    """Handle chat without decision tools (RAG only)."""
    user_input = request.args.get('userMessage', '')
    conversation_id = request.args.get('conversationId', '')
    if not user_input:
        return jsonify({"input": "", "output": "Please provide a message", "type": "error"})
    
    result = workflow_service.process_message(
        user_input, 
        use_decision_engine=False,
        conversation_id=conversation_id
    )
    return jsonify(result)

@chat_bp.route('/start_conversation', methods=['GET'])
def start_conversation():
    """Start a new conversation and return a conversation ID."""
    conversation_id = str(uuid.uuid4())
    return jsonify({
        "conversation_id": conversation_id,
        "message": "Conversation started",
        "status": "success"
    })

@chat_bp.route('/inspect_memory', methods=['GET'])
def inspect_memory():
    """Inspect the conversation memory for a given conversation ID."""
    conversation_id = request.args.get('conversationId', '')
    if not conversation_id:
        return jsonify({"status": "error", "message": "Conversation ID is required"}), 400
    if conversation_id not in workflow_service.conversations:
        return jsonify({
            "status": "error",
            "message": f"No memory found for conversation ID: {conversation_id}",
            "available_conversations": list(workflow_service.conversations.keys())
        }), 404
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
    """Reset the conversation memory for a specified conversation ID."""
    conversation_id = request.args.get('conversationId', '')
    if not conversation_id:
        return jsonify({"status": "error", "message": "Conversation ID is required"}), 400
    if conversation_id in workflow_service.conversations:
        del workflow_service.conversations[conversation_id]
    workflow_service.get_or_create_memory(conversation_id)
    return jsonify({
        "status": "success",
        "message": f"Memory reset for conversation: {conversation_id}"
    })

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "llm": llm_service.llm.__class__.__name__ if llm_service.llm else "Not initialized",
        "rag_initialized": rag_service.chain is not None if hasattr(rag_service, 'chain') else False,
        "langsmith_configured": langsmith_client is not None
    }
    return jsonify(status)

# ----------------------------
# New Endpoint: PDF Upload via Chat
# ----------------------------
@chat_bp.route('/upload_pdf', methods=['POST', 'OPTIONS'])
def chat_upload_pdf():
    # Handle CORS pre-flight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")  # Allow all headers
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
    print("00.1")

    # Extract query parameters from URL
    conversation_id = request.args.get('conversationId', '')
    prompt_value = request.args.get('prompt', '')
    print(f"Processing upload with conversation ID: {conversation_id}, prompt: {prompt_value}")
    
    # Validate file upload
    if 'form_file' not in request.files:
        print("No file part in request")
        return jsonify({"success": False, "error": "No file part"}), 400
    
    file = request.files['form_file']
    if file.filename == "":
        print("No selected file")
        return jsonify({"success": False, "error": "No selected file"}), 400

    print(f"File received: {file.filename}")
    
    # Secure the filename and determine S3 file path
    filename = secure_filename(file.filename)
    file_path = f"ocr-renewal/{filename}"
    print("0.1 - Secured filename")
    
    # Upload the file to S3
    upload_status = uploadFileinS3(file, file_path)
    if isinstance(upload_status, dict) and upload_status.get("error"):
        print(f"S3 upload error: {upload_status.get('error')}")
        return jsonify({"success": False, "error": upload_status.get("error")}), 500
    
    print("0.2 - File uploaded to S3")
    
    # Create a tracking ID and generate the Kafka message.
    tracking_id = str(uuid.uuid4())
    print(f"0.3 - Tracking ID: {tracking_id}")

    query_field = 'ocr-renewal-queries/MASS_571_RENEWAL_QUERIES.txt'
    kafka_message = generate_message(file_path, query_field, tracking_id)
    print("0.4 - Kafka message generated")
    print(kafka_message)
    print(tracking_id)
    send_message(kafka_message, tracking_id)
    print("0.5 - Message sent to Kafka")
    
    # Consume OCR result from Kafka
    print(f"Waiting for OCR result from topic: {config.KFKA_CONSUMER_TOPIC_NAME}")
    ocr_result = consume_messages(config.KFKA_CONSUMER_TOPIC_NAME, 1.0, tracking_id)
    print("0.6 - OCR result received")
    
    if not ocr_result:
        print("OCR processing timed out or failed")
        return jsonify({"success": False, "error": "OCR processing timed out or failed"}), 500

    # Transform the OCR result into structured data
    final_ocr_data = transform_ocr_result(ocr_result)
    print(f"Final OCR data: {final_ocr_data}")
    # final_ocr_data= {
    #        "ContractNumber": "571003597",
    #         "EmailAddress": "meandme@gmail.com",
    #         "GuaranteePeriod": "3 year",
    #         "OwnerName": "mehul sarams",
    #         "OwnerSignatureDate": "26/3/25",
    #         "PhoneNumber": "1-866-645-2362"
    # }

    # Process the message with the workflow service
    result = workflow_service.process_message(
        user_input=prompt_value,
        use_decision_engine=True,
        conversation_id=conversation_id,
        ocr_data=final_ocr_data
    )

    # Add CORS headers to the response
    response = jsonify(result)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response