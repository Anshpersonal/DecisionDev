# app/controllers/form_controller.py - Controller for form processing

import os
import uuid
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from app.model.form_model import FormData
from app.service.langchain_service import LangChainService
from app.service.ocr_service import OCRService
from app.service.validation_service import ValidationService
from app.service.lc_api_service import APIService
from app.service.lc_validation_service import ComparisonService
from app.service.update_lc_service import UpdateService
from app.config import Config
import boto3
from confluent_kafka import Producer, Consumer

config = Config()

# Create blueprint
form_bp = Blueprint('form', __name__)

S3_BUCKET = config.S3_BUCKET
s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region_name=config.region_name
)

# Kafka Producer Configuration with Authentication
producer_config = {
    "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": config.KAFKA_API_KEY,
    "sasl.password": config.KAFKA_API_SECRET
}

# Consumer Configuration
consumer_config = {
    "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": config.KAFKA_API_KEY,
    "sasl.password": config.KAFKA_API_SECRET,
    "group.id": config.KAFKA_CONSUMER_GROUP_ID,
    "auto.offset.reset": "earliest"  # Start from beginning if no previous offset
}

producer = Producer(producer_config)

alias_mapping = {
    "contract-number": "contractNumber",
    "owner-signature-date": "ownerSignatureDate",
    "subsequent-guarantee-period": "guaranteePeriod",
    "owner-name": "ownerName",
    "owner-email-address": "emailAddress",
    "owner-phone-number": "phoneNumber"
}

# Initialize services
langchain_service = None
ocr_service = None
validation_service = None
api_service = None
comparison_service = None
update_service = None
workflow_service = None


@form_bp.before_app_request
def initialize_services():
    """Initialize all services before first request"""
    global langchain_service, ocr_service, validation_service, workflow_service, api_service, comparison_service, update_service
    
    # Initialize LangChain service
    langchain_service = LangChainService(config)
    components = langchain_service.initialize()
    llm = components["llm"]
    
    # Initialize OCR service
    ocr_service = OCRService(config.OCR_API_ENDPOINT)
    
    # Initialize validation service
    validation_service = ValidationService(llm)
    
    # Initialize API service
    api_service = APIService(config.API_BASE_URL)
    
    # Initialize comparison service
    comparison_service = ComparisonService(llm)
    
    # Initialize update service
    update_service = UpdateService(config.API_BASE_URL)
    
    # Initialize workflow service with LangGraph
    from app.service.workflow_service import WorkflowService
    workflow_service = WorkflowService(
        ocr_service, 
        validation_service,
        api_service,
        comparison_service,
        update_service,
        llm
    )


# Legacy Web UI Routes
@form_bp.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@form_bp.route('/upload', methods=['POST'])
def upload_form():
    """Handle form upload and validation"""
    # Check if form type was selected
    form_type = request.form.get('form_type')
    print(form_type)
    if not form_type:
        flash('Please select a form type', 'error')
        return redirect(url_for('form.index'))
    
    # Check if it's a test submission
    is_test = 'test_mode' in request.form
    
    if is_test:
        # Process as test form
        return process_test_form(form_type)
    else:
        # Check if file was included
        if 'form_file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('form.index'))
        
        file = request.files['form_file']
        print('File=====')
        print(file)
        
        # Check if user selected a file
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('form.index'))
        
        # Process actual file
        if file:
            filename = secure_filename(file.filename)
            file_path='ocr-renewal/'
            
            uploadFileinS3(file, file_path+filename)
            print("File uploaded successfully")
            trackingid=str(uuid.uuid4())
            message=generate_message(file_path+filename, 'ocr-renewal-queries/MASS_571_RENEWAL_QUERIES.txt', trackingid)
            print("message created============")
            print(message)
            send_message(message, trackingid)
            ocr_result= consume_messages(config.KFKA_CONSUMER_TOPIC_NAME, 1.0, trackingid)
            print("OCR results====")
            print(ocr_result)
            final_result_ocr=transform_ocr_result(ocr_result)
            print("final_result_ocr=====")
            print(final_result_ocr)
            
            return process_form(form_type, final_result_ocr)

# New API Routes for Chatbot Interface

@form_bp.route('/api/chat/start', methods=['POST'])
def chat_start():
    """Initialize chat session"""
    session_id = str(uuid.uuid4())
    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": "Hello welcome to MAAS.AI... \nWould you like to validate a Renewals form or a Withdrawals application?"
    })

@form_bp.route('/api/chat/form_options', methods=['POST'])
def chat_form_options():
    """Return form type options"""
    return jsonify({
        "success": True,
        "form_types": ["renewals", "withdrawals"],
        "message": "Please select the type of form you'd like to validate."
    })

@form_bp.route('/api/chat/upload_options', methods=['POST'])
def chat_upload_options():
    """Return upload options"""
    return jsonify({
        "success": True,
        "upload_options": ["upload", "test"],
        "message": "Would you like to upload a form or use test data?"
    })

@form_bp.route('/api/chat/upload', methods=['POST'])
def chat_upload_form():
    """Handle form upload from chat interface"""
    try:
        # Check form type
        form_type = request.form.get('form_type')
        if not form_type:
            return jsonify({
                "success": False,
                "error": "Form type is required"
            }), 400
        
        # Check file
        if 'form_file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file part"
            }), 400
            
        file = request.files['form_file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No selected file"
            }), 400
        
        print("test 1")    
        print(file.filename)
        # Process file
        filename = secure_filename(file.filename)
        file_path = 'ocr-renewal/'
        
        # Upload to S3
        uploadFileinS3(file, file_path+filename)
        
        # Create tracking ID
        tracking_id = str(uuid.uuid4())
        
        # Generate and send Kafka message
        message = generate_message(
            file_path+filename, 
            'ocr-renewal-queries/MASS_571_RENEWAL_QUERIES.txt', 
            tracking_id
        )
        print("test 1.2")   
        print(tracking_id)
        send_message(message, tracking_id)
        print("test 1.3")  
        
        # Consume OCR result
        ocr_result = consume_messages(config.KFKA_CONSUMER_TOPIC_NAME, 1.0, tracking_id)
        print("test 1.4")
        
        print(ocr_result)
        print(tracking_id)
        # Transform OCR result
        final_result_ocr = transform_ocr_result(ocr_result)
        print(final_result_ocr)
        # Get vector DB
        vector_db = langchain_service.get_vector_db()
       
        print("test 2")   
        # Run the workflow
        result = workflow_service.run_workflow(
            form_data={"path": final_result_ocr},
            form_type=form_type,
            vector_db=vector_db,
            is_test=False
        )
        
        # Check for errors
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result.get("error")
            }), 500
        
        # Prepare response
        response = {
            "success": True,
            "response": result["response"],
            "form_type": form_type,
            "extracted_data": result["json_data"],
            "validation_result": result["validation_details"]
        }
        
        # Add additional data if available
        if "db_data" in result:
            response["db_data"] = result["db_data"]
        
        if "comparison_result" in result:
            response["comparison_result"] = result["comparison_result"]
            
        if "update_result" in result:
            response["update_result"] = result["update_result"]
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in transform_ocr_result: {str(e)}") 
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@form_bp.route('/api/chat/process_test', methods=['POST'])
def chat_process_test():
    """Process test form from chat interface"""
    try:
        # Get form type from request
        data = request.json
        form_type = data.get('form_type')
        
        if not form_type:
            return jsonify({
                "success": False,
                "error": "Form type is required"
            }), 400
        
        # Get vector DB
        vector_db = langchain_service.get_vector_db()
        
        # Run the workflow with test flag
        result = workflow_service.run_workflow(
            form_data={"path": "test_form.pdf"},
            form_type=form_type,
            vector_db=vector_db,
            is_test=True
        )
        
        # Check for errors
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result.get("error")
            }), 500
        
        # Prepare response
        response = {
            "success": True,
            "response": result["response"],
            "form_type": form_type,
            "extracted_data": result["json_data"],
            "validation_result": result["validation_details"],
            "is_test": True
        }
        
        # Add additional data if available
        if "db_data" in result:
            response["db_data"] = result["db_data"]
        
        if "comparison_result" in result:
            response["comparison_result"] = result["comparison_result"]
            
        if "update_result" in result:
            response["update_result"] = result["update_result"]
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Helper Functions

def process_form(form_type, final_result_ocr):
    """
    Process an uploaded form file using the LangGraph workflow
    
    Args:
        form_type (str): Type of form
        file_path (str): Path to the form file
        
    Returns:
        Response: Rendered template with results
    """
    try:
        # Get vector DB
        vector_db = langchain_service.get_vector_db()
        
        # Run the workflow
        result = workflow_service.run_workflow(
            form_data={"path": final_result_ocr},
            form_type=form_type,
            vector_db=vector_db,
            is_test=False
        )
        
        # Check for errors
        if "error" in result:
            flash(f"Error processing form: {result.get('error')}", 'error')
            return redirect(url_for('form.index'))
        
        # Prepare template variables
        template_vars = {
            "response": result["response"],
            "form_type": form_type,
            "extracted_data": result["json_data"],
            "validation_result": result["validation_details"]
        }
        
        # Add DB data and comparison results if available
        if "db_data" in result:
            template_vars["db_data"] = result["db_data"]
        
        if "comparison_result" in result:
            template_vars["comparison_result"] = result["comparison_result"]
            
        if "update_result" in result:
            template_vars["update_result"] = result["update_result"]
        
        return render_template('result.html', **template_vars)
    
    except Exception as e:
        flash(f"Error processing form: {str(e)}", 'error')
        return redirect(url_for('form.index'))

def process_test_form(form_type):
    """
    Process a test form submission using the LangGraph workflow
    
    Args:
        form_type (str): Type of form
        
    Returns:
        Response: Rendered template with results
    """
    try:
        # Get vector DB
        vector_db = langchain_service.get_vector_db()
        print("executed process test form")
      
        # Run the workflow with test flag
        result = workflow_service.run_workflow(
            form_data={"path": "test_form.pdf"},
            form_type=form_type,
            vector_db=vector_db,
            is_test=True
        )
        
        # Check for errors
        if "error" in result:
            flash(f"Error with test form: {result.get('error')}", 'error')
            return redirect(url_for('form.index'))
        
        # Prepare template variables
        template_vars = {
            "response": result["response"],
            "form_type": form_type,
            "extracted_data": result["json_data"],
            "validation_result": result["validation_details"],
            "is_test": True
        }
        
        # Add DB data and comparison results if available
        if "db_data" in result:
            template_vars["db_data"] = result["db_data"]
        
        if "comparison_result" in result:
            template_vars["comparison_result"] = result["comparison_result"]
            
        if "update_result" in result:
            template_vars["update_result"] = result["update_result"]
        
        return render_template('result.html', **template_vars)
    
    except Exception as e:
        flash(f"Error processing test form: {str(e)}", 'error')
        return redirect(url_for('form.index'))

@form_bp.route('/api/validate', methods=['POST'])
def api_validate_form():
    """API endpoint for form validation"""
    data = request.json
    form_type = data.get('form_type')
    file_path = data.get('file_path')
    is_test = data.get('is_test', False)
    
    try:
        if is_test:
            extracted_data = ocr_service.extract_test_data(form_type)
        else:
            extracted_data = ocr_service.extract_form_data(file_path)
            
        vector_db = langchain_service.get_vector_db()
        rules = vector_db.retrieve_validation_rules(form_type)
        
        validation_result = validation_service.validate_form_data(
            extracted_data, rules, form_type
        )
        
        response = validation_result.get_formatted_response(form_type)
        
        # If validation passed, fetch database data
        db_data = None
        comparison_result = None
        update_result = None
        
        if validation_result.valid:
            # Get ID field based on form type
            id_field = "ContractNumber" if form_type == "wenewals" else "withdrawals"
            form_id = extracted_data.get(id_field)
            
            if form_id:
                # Fetch data from database
                db_data = api_service.fetch_data_by_form_type(form_type, form_id)
                
                # Compare with extracted data
                if "error" not in db_data:
                    comparison_result = comparison_service.compare_data(
                        extracted_data, db_data, form_type
                    )
                    
                    # Update database if comparison passed
                    if comparison_result.get("matches", False):
                        update_result = update_service.update_database(
                            form_type, extracted_data, validation_result.to_dict(), comparison_result
                        )
        
        result = {
            "success": True,
            "response": response,
            "form_type": form_type,
            "extracted_data": extracted_data,
            "validation_result": validation_result.to_dict()
        }
        
        # Add additional data if available
        if db_data:
            result["db_data"] = db_data
        
        if comparison_result:
            result["comparison_result"] = comparison_result
            
        if update_result:
            result["update_result"] = update_result
            
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

def uploadFileinS3(file, file_name):
    s3_client.upload_fileobj(file, S3_BUCKET, file_name)
    try:
        s3_client.upload_fileobj(file=file, S3_BUCKET=S3_BUCKET, file_key=file.filename)
        return "File uploaded successfully"
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_message(message, tracking_id):
    producer.produce(config.KAFKA_TOPIC, key=tracking_id, value=message)
    producer.flush()

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
        }),  # Convert `data` to string
        "identifier": [
            {
                "trackingId": tracking_id
            }
        ]
    }
    
    return json.dumps(data, indent=4)

def consume_messages(topic, timeout, tracking_id):
    message_obj = None
    """
    Function to consume messages from a Kafka topic.
    :param topic: Kafka topic name
    :param timeout: Polling timeout in seconds
    """
    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])
    
    print(f"Listening for messages on topic: {topic}...")

    try:
        while True:
            msg = consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            key = msg.key().decode() if msg.key() else "No Key"
            value = json.loads(msg.value().decode())
           
            # Decode the 'data' field (which is a string) to a nested dictionary
            message_obj = json.loads(value["data"])
            if value["identifier"][0]["trackingId"] == tracking_id:
                consumer.close()
                return message_obj
             
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        consumer.close()    
    return message_obj

def transform_ocr_result(ocr_result):
    transformed_data = {}
    for item in ocr_result.get("extractionResults", []):
        alias = item.get("queryAlias")
        if alias in alias_mapping and item.get("queryResults"):
            transformed_data[alias_mapping[alias]] = item["queryResults"][0].get("queryAnswer", "")
    return transformed_data