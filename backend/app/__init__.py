"""
SOAR Platform - Flask Application Factory
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import get_config
from app.database.db import init_db, db
from app.utils.logging_setup import setup_logging
import logging

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application Factory Pattern
    Creates and configures the Flask application
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    # NEW: Use the local variable 'config_name'
    logger.info(f"Starting SOAR Platform in {config_name} mode")
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": app.config['CORS_SUPPORTS_CREDENTIALS']
        }
    })
    logger.info("CORS enabled")
    
    # Initialize database
    init_db(app)
    logger.info("Database initialized")
    
    # Register blueprints (routes)
    register_blueprints(app)
    logger.info("Blueprints registered")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'SOAR Platform API',
            'version': app.config['API_VERSION']
        }), 200
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'environment': app.config['FLASK_ENV'],
            'endpoints': {
                'alerts': f"{app.config['API_PREFIX']}/alerts",
                'incidents': f"{app.config['API_PREFIX']}/incidents",
                'playbooks': f"{app.config['API_PREFIX']}/playbooks",
                'analytics': f"{app.config['API_PREFIX']}/analytics"
            }
        }), 200
    
    logger.info("SOAR Platform initialized successfully")
    
    return app


def register_blueprints(app):
    """Register all blueprints (route modules)"""
    from app.routes import alerts
    
    # Register alert routes
    # OLD: app.register_blueprint(alerts.bp)
    # NEW: Add the '/api/v1' prefix here to combine with the blueprint's '/alerts'
    app.register_blueprint(alerts.bp)
    logger.info("Alert routes registered")
    
    # TODO: Register other blueprints when created
    # from app.routes import incidents, playbooks, analytics
    # app.register_blueprint(incidents.bp)
    # app.register_blueprint(playbooks.bp)
    # app.register_blueprint(analytics.bp)


def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'error': 'Resource not found',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        db.session.rollback()  # Rollback any failed database transactions
        return jsonify({
            'status': 'error',
            'error': 'Internal server error',
            'code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'error': 'Bad request',
            'code': 400
        }), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'status': 'error',
            'error': 'Forbidden',
            'code': 403
        }), 403
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'error': 'Method not allowed',
            'code': 405
        }), 405