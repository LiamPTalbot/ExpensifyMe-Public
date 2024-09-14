import os
from flask import Flask
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load environment variables from .env file
    load_dotenv()

    # Set default configuration values
    app.config.from_mapping(
        SECRET_KEY='************************************************',
        DATABASE=os.path.join(app.instance_path, 'ExpensifyMe.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        ALLOWED_EXTENSIONS={'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'},
        FORM_RECOGNIZER_ENDPOINT=os.getenv('FORM_RECOGNIZER_ENDPOINT'),
        FORM_RECOGNIZER_API_KEY=os.getenv('FORM_RECOGNIZER_API_KEY')
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Azure Form Recognizer client
    app.document_analysis_client = DocumentAnalysisClient(
        app.config['FORM_RECOGNIZER_ENDPOINT'],
        AzureKeyCredential(app.config['FORM_RECOGNIZER_API_KEY'])
    )

    # Import and initialize database functionality
    from . import db
    db.init_app(app)

    # Register authentication and main route blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from .routes import main
    app.register_blueprint(main)

    return app
