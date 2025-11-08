"""
Input Validation Utilities
Validates and sanitizes user input
"""
import re
from functools import wraps
from flask import request, jsonify
from .logging_setup import security_logger, setup_logging


def validate_required_fields(required_fields):
    """
    Decorator to validate required fields in request data
    
    Usage:
        @validate_required_fields(['title', 'severity'])
        def create_alert():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_severity(severity):
    """Validate severity level"""
    valid_severities = ['low', 'medium', 'high', 'critical']
    if severity.lower() not in valid_severities:
        raise ValueError(f"Invalid severity. Must be one of: {', '.join(valid_severities)}")
    return severity.lower()


def validate_status(status, valid_statuses):
    """Validate status against allowed values"""
    if status.lower() not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    return status.lower()


def validate_ip_address(ip):
    """Validate IPv4 or IPv6 address"""
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if not (re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)):
        raise ValueError("Invalid IP address format")
    
    # Validate IPv4 octets
    if '.' in ip:
        octets = ip.split('.')
        for octet in octets:
            if int(octet) > 255:
                raise ValueError("Invalid IPv4 address")
    
    return ip


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def sanitize_string(text, max_length=None):
    """Sanitize string input"""
    if not text:
        return text
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_pagination(page, per_page, max_per_page=100):
    """Validate pagination parameters"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > max_per_page:
            per_page = max_per_page
        
        return page, per_page
    except ValueError:
        return 1, 20


def validate_json_field(data, field_name):
    """Validate that a field contains valid JSON"""
    import json
    
    if field_name not in data:
        return None
    
    value = data[field_name]
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"{field_name} must be valid JSON")
    
    return value # <--- FIX: This is the correct end of the function.