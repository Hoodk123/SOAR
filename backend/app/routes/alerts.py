"""
Alert Routes - API endpoints for alert management
"""
from flask import Blueprint, request, jsonify
from app.services.alert_service import AlertService
# NEW Imports (You need to list the functions explicitly since they are not in validators.py)
from app.utils.validators import validate_required_fields, validate_severity, validate_pagination
# You will likely need to create a helper file for responses too
from app.utils.response_helpers import build_response, build_error_response 
import logging

logger = logging.getLogger(__name__) # Keep this line

# Create blueprint
bp = Blueprint('alerts', __name__, url_prefix='/api/v1/alerts')


@bp.route('', methods=['GET'])
def get_alerts():
    """
    Get all alerts with optional filters
    
    Query Parameters:
        - severity: Filter by severity (low, medium, high, critical)
        - status: Filter by status (open, investigating, resolved, closed)
        - source: Filter by source (SIEM, EDR, etc.)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        200: Paginated list of alerts
    """
    try:
        # Parse query parameters
        filters = {}
        if request.args.get('severity'):
            filters['severity'] = request.args.get('severity')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('source'):
            filters['source'] = request.args.get('source')
        if request.args.get('ip_address'):
            filters['ip_address'] = request.args.get('ip_address')
        
        # Pagination
        page, per_page = validate_pagination(
            request.args.get('page'),
            request.args.get('per_page')
        )
        
        # Get alerts
        pagination = AlertService.get_all_alerts(filters, page, per_page)
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """
    Get a specific alert by ID
    
    Returns:
        200: Alert details
        404: Alert not found
    """
    try:
        alert = AlertService.get_alert(alert_id)
        return jsonify(alert.to_dict()), 200
        
    except ValueError as e:
        return build_error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('', methods=['POST'])
@validate_required_fields(['title', 'severity', 'source'])
def create_alert():
    """
    Create a new alert
    
    Required fields:
        - title: Alert title
        - severity: Alert severity (low, medium, high, critical)
        - source: Alert source
    
    Optional fields:
        - description: Alert description
        - ip_address: Source IP address
        - hostname: Source hostname
        - raw_data: Raw alert data (JSON)
    
    Returns:
        201: Alert created successfully
        400: Invalid input
    """
    try:
        data = request.get_json()
        
        # Validate severity
        data['severity'] = validate_severity(data['severity'])
        
        # Create alert
        alert = AlertService.create_alert(data)
        
        return build_response(
            data=alert.to_dict(),
            message='Alert created successfully',
            status_code=201
        )
        
    except ValueError as e:
        return build_error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """
    Update an existing alert
    
    Updatable fields:
        - status: Alert status
        - description: Alert description
        - severity: Alert severity
        - assigned_to: Assigned user ID
    
    Returns:
        200: Alert updated successfully
        404: Alert not found
        400: Invalid input
    """
    try:
        data = request.get_json()
        
        # Validate severity if provided
        if 'severity' in data:
            data['severity'] = validate_severity(data['severity'])
        
        # Update alert
        alert = AlertService.update_alert(alert_id, data)
        
        return build_response(
            data=alert.to_dict(),
            message='Alert updated successfully'
        )
        
    except ValueError as e:
        return build_error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """
    Delete an alert
    
    Returns:
        200: Alert deleted successfully
        404: Alert not found
    """
    try:
        AlertService.delete_alert(alert_id)
        
        return build_response(
            message=f'Alert {alert_id} deleted successfully'
        )
        
    except ValueError as e:
        return build_error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get alert statistics
    
    Returns:
        200: Statistics object with counts and metrics
    """
    try:
        stats = AlertService.get_alert_statistics()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/search', methods=['GET'])
def search_alerts():
    """
    Search alerts by title or description
    
    Query Parameters:
        - q: Search query
    
    Returns:
        200: List of matching alerts
    """
    try:
        search_term = request.args.get('q', '')
        
        if not search_term:
            return build_error_response('Search query required', 400)
        
        alerts = AlertService.search_alerts(search_term)
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching alerts: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/<int:alert_id>/escalate', methods=['POST'])
def escalate_alert(alert_id):
    """
    Escalate alert severity
    
    Returns:
        200: Alert escalated successfully
        404: Alert not found
    """
    try:
        alert = AlertService.escalate_alert(alert_id)
        
        return build_response(
            data=alert.to_dict(),
            message=f'Alert escalated to {alert.severity}'
        )
        
    except ValueError as e:
        return build_error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error escalating alert {alert_id}: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/<int:alert_id>/timeline', methods=['GET'])
def get_alert_timeline(alert_id):
    """
    Get timeline of events for an alert
    
    Returns:
        200: Timeline events
        404: Alert not found
    """
    try:
        timeline = AlertService.get_alert_timeline(alert_id)
        
        return jsonify({
            'alert_id': alert_id,
            'timeline': timeline
        }), 200
        
    except ValueError as e:
        return build_error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error getting timeline for alert {alert_id}: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/bulk-update', methods=['POST'])
@validate_required_fields(['alert_ids', 'status'])
def bulk_update_alerts():
    """
    Update status for multiple alerts
    
    Required fields:
        - alert_ids: List of alert IDs
        - status: New status
    
    Returns:
        200: Alerts updated successfully
        400: Invalid input
    """
    try:
        data = request.get_json()
        alert_ids = data['alert_ids']
        new_status = data['status']
        
        count = AlertService.bulk_update_status(alert_ids, new_status)
        
        return build_response(
            message=f'{count} alerts updated to {new_status}'
        )
        
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        return build_error_response(str(e), 500)


@bp.route('/sources', methods=['GET'])
def get_sources():
    """
    Get alert counts by source
    
    Returns:
        200: Dictionary of source counts
    """
    try:
        sources = AlertService.get_alerts_by_source()
        return jsonify(sources), 200
        
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        return build_error_response(str(e), 500)