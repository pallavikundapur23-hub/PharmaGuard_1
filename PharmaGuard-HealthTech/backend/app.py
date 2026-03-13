from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Flask app factory"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_VCF_FILE_SIZE', 5242880))  # 5MB

    # Enable CORS for React frontend
    CORS(app, resources={r"/api/*": {"origins": os.getenv('FRONTEND_URL', '*')}})

    # Register blueprints
    from backend.routes.health import health_bp
    from backend.routes.analysis import analysis_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(analysis_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
