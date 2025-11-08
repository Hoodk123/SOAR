"""
Database connection and management
Handles SQLAlchemy initialization and session management
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask app
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they're registered
        from app.models import alert, incident, playbook, execution_log, user
        
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Seed demo data in development
        if app.config['DEBUG']:
            seed_demo_data()


def get_db():
    """Get database session (for use in routes)"""
    return db.session


@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations
    
    Usage:
        with session_scope() as session:
            user = User(name='John')
            session.add(user)
            # Automatically commits on success, rolls back on error
    """
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()


def seed_demo_data():
    """Populate database with demo data for development"""
    from app.models.alert import Alert
    from app.models.playbook import Playbook
    from app.models.incident import Incident
    from datetime import datetime, timedelta
    import json
    
    try:
        # Check if data already exists
        if Alert.query.first():
            logger.info("Demo data already exists, skipping seed")
            return
        
        logger.info("Seeding demo data...")
        
        # Create demo alerts
        alerts = [
            Alert(
                title='Suspicious Login Attempt',
                severity='high',
                source='SIEM',
                status='open',
                ip_address='192.168.1.100',
                description='Multiple failed login attempts detected from unusual location',
                timestamp=datetime.utcnow(),
                raw_data=json.dumps({'attempts': 5, 'location': 'Unknown'})
            ),
            Alert(
                title='Malware Detected',
                severity='critical',
                source='EDR',
                status='open',
                ip_address='10.0.0.45',
                description='Trojan.Generic detected on workstation W-1024',
                timestamp=datetime.utcnow() - timedelta(hours=1),
                raw_data=json.dumps({'malware_type': 'Trojan', 'file': 'suspicious.exe'})
            ),
            Alert(
                title='Unusual Network Traffic',
                severity='medium',
                source='Firewall',
                status='open',
                ip_address='172.16.0.20',
                description='High volume data transfer to unknown destination',
                timestamp=datetime.utcnow() - timedelta(hours=2),
                raw_data=json.dumps({'bytes_transferred': 1073741824, 'destination': '203.0.113.1'})
            ),
            Alert(
                title='Phishing Email Detected',
                severity='high',
                source='Email Gateway',
                status='resolved',
                ip_address='N/A',
                description='Malicious link in email detected and quarantined',
                timestamp=datetime.utcnow() - timedelta(hours=3),
                raw_data=json.dumps({'sender': 'phishing@evil.com', 'subject': 'Urgent: Verify Account'})
            ),
            Alert(
                title='Privilege Escalation Attempt',
                severity='critical',
                source='SIEM',
                status='investigating',
                ip_address='10.0.0.155',
                description='Unauthorized attempt to gain admin privileges',
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                raw_data=json.dumps({'user': 'john.doe', 'target_privilege': 'Administrator'})
            )
        ]
        
        for alert in alerts:
            db.session.add(alert)
        
        # Create demo playbooks
        playbooks = [
            Playbook(
                name='Malware Response',
                description='Automated response workflow for malware detection',
                trigger_condition='severity:critical AND source:EDR',
                steps=json.dumps([
                    {'order': 1, 'action': 'isolate_host', 'description': 'Isolate infected host from network'},
                    {'order': 2, 'action': 'scan_system', 'description': 'Run full system malware scan'},
                    {'order': 3, 'action': 'collect_evidence', 'description': 'Collect forensic evidence'},
                    {'order': 4, 'action': 'remove_threat', 'description': 'Remove or quarantine malware'},
                    {'order': 5, 'action': 'generate_report', 'description': 'Generate incident report'},
                    {'order': 6, 'action': 'notify_team', 'description': 'Notify security team'}
                ]),
                active=True
            ),
            Playbook(
                name='Phishing Investigation',
                description='Investigate and respond to phishing attempts',
                trigger_condition='source:Email Gateway',
                steps=json.dumps([
                    {'order': 1, 'action': 'block_sender', 'description': 'Block sender email address'},
                    {'order': 2, 'action': 'analyze_email', 'description': 'Analyze email headers and content'},
                    {'order': 3, 'action': 'check_similar', 'description': 'Search for similar emails'},
                    {'order': 4, 'action': 'notify_users', 'description': 'Alert affected users'},
                    {'order': 5, 'action': 'update_filters', 'description': 'Update email filters'}
                ]),
                active=True
            ),
            Playbook(
                name='Brute Force Attack Response',
                description='Handle brute force authentication attempts',
                trigger_condition='type:authentication AND severity:high',
                steps=json.dumps([
                    {'order': 1, 'action': 'lock_account', 'description': 'Temporarily lock affected account'},
                    {'order': 2, 'action': 'block_ip', 'description': 'Block source IP address'},
                    {'order': 3, 'action': 'verify_user', 'description': 'Contact user to verify activity'},
                    {'order': 4, 'action': 'reset_credentials', 'description': 'Force password reset'},
                    {'order': 5, 'action': 'enable_mfa', 'description': 'Enable multi-factor authentication'},
                    {'order': 6, 'action': 'update_logs', 'description': 'Document incident in logs'}
                ]),
                active=True
            ),
            Playbook(
                name='Data Exfiltration Response',
                description='Respond to potential data exfiltration',
                trigger_condition='severity:critical AND type:data_transfer',
                steps=json.dumps([
                    {'order': 1, 'action': 'block_connection', 'description': 'Block outbound connection'},
                    {'order': 2, 'action': 'identify_data', 'description': 'Identify data being transferred'},
                    {'order': 3, 'action': 'isolate_system', 'description': 'Isolate affected system'},
                    {'order': 4, 'action': 'forensic_analysis', 'description': 'Perform forensic analysis'},
                    {'order': 5, 'action': 'notify_legal', 'description': 'Notify legal and compliance teams'},
                    {'order': 6, 'action': 'assess_impact', 'description': 'Assess data breach impact'}
                ]),
                active=True
            )
        ]
        
        for playbook in playbooks:
            db.session.add(playbook)
        
        # Create demo incidents
        incidents = [
            Incident(
                title='Ransomware Attack Investigation',
                severity='critical',
                status='investigating',
                priority='critical',
                description='Multiple systems showing ransomware infection',
                assignee='Security Team Alpha',
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            Incident(
                title='Insider Threat Detection',
                severity='high',
                status='new',
                priority='high',
                description='Suspicious data access patterns detected',
                assignee='SOC Team',
                created_at=datetime.utcnow() - timedelta(hours=6)
            )
        ]
        
        for incident in incidents:
            db.session.add(incident)
        
        db.session.commit()
        logger.info(f"Demo data seeded: {len(alerts)} alerts, {len(playbooks)} playbooks, {len(incidents)} incidents")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding demo data: {str(e)}")
        raise


def reset_database():
    """Drop all tables and recreate (USE WITH CAUTION!)"""
    logger.warning("Resetting database - all data will be lost!")
    db.drop_all()
    db.create_all()
    seed_demo_data()
    logger.info("Database reset complete")