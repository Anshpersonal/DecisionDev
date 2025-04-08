# # app/__init__.py - Flask application factory

from flask import Flask
from .config import Config
from app.controller.form_controller import form_bp
from flask_cors import CORS


def create_app(config_class=Config):
    """Create and configure the Flask application"""


    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(form_bp)


    # Ensure upload directory exists
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register template filters
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        return s.replace('\n', '<br>') if s else ''
    
    return app
# app/__init__.py - Flask application factory
