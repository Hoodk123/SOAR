# backend/app/utils/response_helpers.py

from flask import jsonify

# --- Helper Functions for API Responses ---

def build_response(data=None, message="Success", status_code=200):
    """
    Standardized function to build a successful JSON API response.
    """
    response = {
        'status': 'success',
        'message': message,
        'data': data if data is not None else {}
    }
    
    # Flask's jsonify automatically handles the content type
    return jsonify(response), status_code

def build_error_response(error_message="An error occurred", status_code=400, errors=None):
    """
    Standardized function to build an error JSON API response.
    
    Args:
        error_message (str): Primary error message.
        status_code (int): HTTP status code (default 400).
        errors (dict/list): Optional detailed error dictionary or list.
    """
    response = {
        'status': 'error',
        'message': error_message,
        'code': status_code,
        'errors': errors if errors is not None else {}
    }
    
    return jsonify(response), status_code