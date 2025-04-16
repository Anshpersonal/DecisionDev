# app/__init__.py - Flask application factory

from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all routes with expanded configuration
    CORS(app, resources={r"/*": {
        "origins": "*",
        "allow_headers": "*",
        "expose_headers": "*",
        "methods": ["GET", "POST"]
    }})
    
    # Register blueprints
    from app.controller.chat_controller import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/rule-agent')
    
    @app.route('/')
    def index():
        return {
            "status": "ok",
            "message": "LangGraph Rule Agent API is running",
            "endpoints": [
                "/rule-agent/chat_with_tools", 
                "/rule-agent/chat_without_tools",
                "/rule-agent/health",
                "/rule-agent/upload_pdf"
            ]
        }
    
    return app