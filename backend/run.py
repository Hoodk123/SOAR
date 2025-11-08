#!/usr/bin/env python3
"""
SOAR Platform - Application Entry Point
Run this file to start the Flask development server
"""
import os
import sys
# --- ADD THESE LINES ---
from dotenv import load_dotenv
# Specify the path to your .env.local file
load_dotenv(dotenv_path='.env.local') 
# -----------------------
# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)

if __name__ == '__main__':
    # Development server settings
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Print startup banner
    print("""""".format(
        config_name,
        host, port,
        'ON' if debug else 'OFF',
        host, port,
        host, port,
        host, port
    ))
    
    # Run development server
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
    except Exception as e:
        print(f"\n✗ Error starting server: {str(e)}")
        sys.exit(1)