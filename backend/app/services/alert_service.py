"""
Alert Service - Business logic for alert management
"""
from app.database.db import db
from app.models.alert import Alert
from app.models.playbook import Playbook
from app.utils import security_logger
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing security alerts"""
    
    @staticmethod
    def create_alert(data):
        """
        Create a new alert
        
        Args:
            data: Alert data dictionary
        
        Returns:
            Alert object
        """
        try:
            alert = Alert.from_dict(data)
            db.session.add(alert)
            db.session.commit()
            
            # Log security event
            security_logger.log_alert(alert)
            
            # Check for auto-trigger playbooks
            if alert.is_critical():
                AlertService._trigger_auto_playbooks(alert)
            
            logger.info(f"Alert created: {alert.id}")
            return alert
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating alert: {str(e)}")
            raise
    
    @staticmethod
    def get_alert(alert_id):
        """Get alert by ID"""
        alert = Alert.query.get(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        return alert
    
    @staticmethod
    def get_all_alerts(filters=None, page=1, per_page=20):
        """
        Get all alerts with optional filters
        
        Args:
            filters: Dictionary of filters (severity, status, source)
            page: Page number
            per_page: Items per page
        
        Returns:
            Paginated query result
        """
        query = Alert.query
        
        if filters:
            if 'severity' in filters:
                query = query.filter(Alert.severity == filters['severity'])
            
            if 'status' in filters:
                query = query.filter(Alert.status == filters['status'])
            
            if 'source' in filters:
                query = query.filter(Alert.source == filters['source'])
            
            if 'ip_address' in filters:
                query = query.filter(Alert.ip_address == filters['ip_address'])
            
            if 'start_date' in filters:
                query = query.filter(Alert.timestamp >= filters['start_date'])
            
            if 'end_date' in filters:
                query = query.filter(Alert.timestamp <= filters['end_date'])
        
        # Order by timestamp descending (newest first)
        query = query.order_by(Alert.timestamp.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def update_alert(alert_id, data):
        """Update an existing alert"""
        try:
            alert = AlertService.get_alert(alert_id)
            
            # Update allowed fields
            allowed_fields = ['status', 'description', 'severity', 'assigned_to']
            for field in allowed_fields:
                if field in data:
                    setattr(alert, field, data[field])
            
            alert.updated_at = datetime.utcnow()
            
            # If status changed to resolved/closed
            if data.get('status') in ['resolved', 'closed']:
                alert.closed_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Alert {alert_id} updated")
            return alert
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating alert {alert_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_alert(alert_id):
        """Delete an alert"""
        try:
            alert = AlertService.get_alert(alert_id)
            db.session.delete(alert)
            db.session.commit()
            logger.info(f"Alert {alert_id} deleted")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting alert {alert_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_alert_statistics():
        """
        Get alert statistics for dashboard
        
        Returns:
            Dictionary with counts and metrics
        """
        total_alerts = Alert.query.count()
        open_alerts = Alert.query.filter_by(status='open').count()
        critical_alerts = Alert.query.filter_by(severity='critical').count()
        
        # Alerts by severity
        severity_counts = {}
        for severity in ['low', 'medium', 'high', 'critical']:
            severity_counts[severity] = Alert.query.filter_by(severity=severity).count()
        
        # Alerts by status
        status_counts = {}
        for status in ['open', 'investigating', 'resolved', 'closed', 'false_positive']:
            status_counts[status] = Alert.query.filter_by(status=status).count()
        
        # Recent alerts (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = Alert.query.filter(Alert.timestamp >= last_24h).count()
        
        return {
            'total': total_alerts,
            'open': open_alerts,
            'critical': critical_alerts,
            'by_severity': severity_counts,
            'by_status': status_counts,
            'last_24_hours': recent_alerts
        }
    
    @staticmethod
    def get_alerts_by_source():
        """Get alert counts grouped by source"""
        from sqlalchemy import func
        
        results = db.session.query(
            Alert.source,
            func.count(Alert.id).label('count')
        ).group_by(Alert.source).all()
        
        return {source: count for source, count in results}
    
    @staticmethod
    def search_alerts(search_term):
        """
        Search alerts by title or description
        
        Args:
            search_term: Search string
        
        Returns:
            List of matching alerts
        """
        search_pattern = f"%{search_term}%"
        alerts = Alert.query.filter(
            (Alert.title.like(search_pattern)) |
            (Alert.description.like(search_pattern))
        ).order_by(Alert.timestamp.desc()).all()
        
        return alerts
    
    @staticmethod
    def escalate_alert(alert_id):
        """Escalate alert severity"""
        try:
            alert = AlertService.get_alert(alert_id)
            alert.escalate_severity()
            db.session.commit()
            
            logger.warning(f"Alert {alert_id} escalated to {alert.severity}")
            security_logger.log_alert(alert)
            
            # Trigger playbooks for new severity level
            AlertService._trigger_auto_playbooks(alert)
            
            return alert
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error escalating alert {alert_id}: {str(e)}")
            raise
    
    @staticmethod
    def bulk_update_status(alert_ids, new_status):
        """Update status for multiple alerts"""
        try:
            alerts = Alert.query.filter(Alert.id.in_(alert_ids)).all()
            
            for alert in alerts:
                alert.update_status(new_status)
            
            db.session.commit()
            logger.info(f"Bulk updated {len(alerts)} alerts to status: {new_status}")
            
            return len(alerts)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in bulk update: {str(e)}")
            raise
    
    @staticmethod
    def _trigger_auto_playbooks(alert):
        """
        Internal method to trigger auto-playbooks
        
        Args:
            alert: Alert object
        """
        try:
            # Find matching playbooks
            playbooks = Playbook.query.filter_by(active=True, auto_trigger=True).all()
            
            for playbook in playbooks:
                if playbook.should_trigger_for_alert(alert):
                    logger.info(f"Auto-triggering playbook {playbook.id} for alert {alert.id}")
                    # Import here to avoid circular import
                    from app.services.playbook_executor import PlaybookExecutor
                    PlaybookExecutor.execute_async(playbook.id, alert.id)
                    
        except Exception as e:
            logger.error(f"Error triggering auto-playbooks: {str(e)}")
    
    @staticmethod
    def get_alert_timeline(alert_id):
        """Get timeline of events for an alert"""
        alert = AlertService.get_alert(alert_id)
        
        timeline = [
            {
                'timestamp': alert.created_at,
                'event': 'Alert Created',
                'description': f"Alert created with severity: {alert.severity}"
            }
        ]
        
        # Add execution logs
        for log in alert.execution_logs:
            timeline.append({
                'timestamp': log.started_at,
                'event': 'Playbook Executed',
                'description': f"Playbook {log.playbook.name} - Status: {log.status}"
            })
        
        if alert.closed_at:
            timeline.append({
                'timestamp': alert.closed_at,
                'event': 'Alert Closed',
                'description': f"Alert closed with status: {alert.status}"
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline