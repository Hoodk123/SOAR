"""
Alert Model - Represents security alerts from various sources
"""
from app.database.db import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class Alert(db.Model):
    """Security Alert Model"""
    
    __tablename__ = 'alerts'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), nullable=False, index=True)  # low, medium, high, critical
    status = db.Column(db.String(50), nullable=False, default='open', index=True)
    
    # Source Information
    source = db.Column(db.String(100), nullable=False, index=True)  # SIEM, EDR, Firewall, etc.
    source_id = db.Column(db.String(255))  # External system alert ID
    
    # Network Information
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    hostname = db.Column(db.String(255))
    mac_address = db.Column(db.String(17))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Additional Data
    raw_data = db.Column(db.Text)  # JSON string of raw alert data
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Relationships
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Execution logs (playbooks run on this alert)
    execution_logs = db.relationship('ExecutionLog', back_populates='alert', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Alert {self.id}: {self.title} ({self.severity})>'
    
    def to_dict(self):
        """Convert alert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'source': self.source,
            'source_id': self.source_id,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'mac_address': self.mac_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'raw_data': self.raw_data,
            'tags': self.tags.split(',') if self.tags else [],
            'incident_id': self.incident_id,
            'assigned_to': self.assigned_to
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create alert from dictionary"""
        return cls(
            title=data.get('title'),
            description=data.get('description'),
            severity=data.get('severity'),
            status=data.get('status', 'open'),
            source=data.get('source'),
            source_id=data.get('source_id'),
            ip_address=data.get('ip_address'),
            hostname=data.get('hostname'),
            mac_address=data.get('mac_address'),
            raw_data=data.get('raw_data'),
            tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags')
        )
    
    def update_status(self, new_status):
        """Update alert status with validation"""
        valid_statuses = ['open', 'investigating', 'resolved', 'closed', 'false_positive']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in ['resolved', 'closed']:
            self.closed_at = datetime.utcnow()
    
    def add_tag(self, tag):
        """Add a tag to the alert"""
        if self.tags:
            tags = set(self.tags.split(','))
            tags.add(tag)
            self.tags = ','.join(tags)
        else:
            self.tags = tag
    
    def remove_tag(self, tag):
        """Remove a tag from the alert"""
        if self.tags:
            tags = set(self.tags.split(','))
            tags.discard(tag)
            self.tags = ','.join(tags) if tags else None
    
    @staticmethod
    def get_severity_priority(severity):
        """Get numeric priority for severity (higher = more severe)"""
        priorities = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return priorities.get(severity.lower(), 0)
    
    def is_critical(self):
        """Check if alert is critical severity"""
        return self.severity.lower() == 'critical'
    
    def is_open(self):
        """Check if alert is still open"""
        return self.status == 'open'
    
    def escalate_severity(self):
        """Escalate alert to next severity level"""
        escalation = {
            'low': 'medium',
            'medium': 'high',
            'high': 'critical',
            'critical': 'critical'
        }
        self.severity = escalation.get(self.severity.lower(), 'critical')
        self.updated_at = datetime.utcnow()