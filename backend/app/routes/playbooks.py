"""
Playbook Routes - API endpoints for playbook management
"""
from flask import Blueprint, request, jsonify
from app.models.playbook import Playbook
from app.database.db import db
import logging
import json

logger = logging.getLogger(__name__)

bp = Blueprint('playbooks', __name__, url_prefix='/api/v1/playbooks')

@bp.route('', methods=['GET'])
def get_playbooks():
    """
    Get all playbooks
    
    Returns:
        200: List of playbooks
    """
    try:
        playbooks = Playbook.query.all()
        return jsonify({
            'playbooks': [pb.to_dict() for pb in playbooks],
            'count': len(playbooks)
        }), 200
    except Exception as e:
        logger.error(f"Error getting playbooks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:playbook_id>', methods=['GET'])
def get_playbook(playbook_id):
    """
    Get a specific playbook by ID
    
    Returns:
        200: Playbook details
        404: Playbook not found
    """
    try:
        playbook = Playbook.query.get(playbook_id)
        if not playbook:
            return jsonify({'error': 'Playbook not found'}), 404
            
        return jsonify(playbook.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting playbook {playbook_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:playbook_id>/execute', methods=['POST'])
def execute_playbook(playbook_id):
    """
    Manually execute a playbook
    
    Returns:
        200: Execution started
        404: Playbook not found
    """
    try:
        playbook = Playbook.query.get(playbook_id)
        if not playbook:
            return jsonify({'error': 'Playbook not found'}), 404
            
        # In a real system, this would trigger an async task (Celery/Redis)
        # For now, we'll simulate a successful start
        
        return jsonify({
            'message': f'Playbook "{playbook.name}" execution started',
            'playbook_id': playbook.id,
            'status': 'running'
        }), 200
    except Exception as e:
        logger.error(f"Error executing playbook {playbook_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
