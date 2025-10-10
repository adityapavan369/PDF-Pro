import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    # SECRET_KEY should be set via environment in production. A dev default is provided
    # for convenience but MUST be changed when deploying.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')
    LOG_FOLDER = os.path.join(os.path.dirname(__file__), 'logs')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
    
    # Application version and environment
    VERSION = os.environ.get('APP_VERSION', '1.0.0')
    ENVIRONMENT = os.environ.get('APP_ENVIRONMENT', 'production')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # External API configuration (example: PDF processing API)
    API_KEY = os.environ.get('PDF_API_KEY', '')
    API_URL = os.environ.get('PDF_API_URL', 'https://api.pdf.co/v1')
    # Admin credentials for basic auth on admin routes. Set these via environment
    # variables in production. Defaults are development-friendly but insecure.
    ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', 'password')

    # Session / cookie hardening settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FOLDER, exist_ok=True)
