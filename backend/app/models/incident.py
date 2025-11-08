"""
Incident Model
Represents security incidents
"""
from datetime import datetime
from app.database.db import db


class Incident(db.Model):
    """Incident model for security incidents"""
    
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='new', index=True)
    priority = db.Column(db.String(50), nullable=False, default='medium', index=True)
    description = db.Column(db.Text, nullable=True)
    assignee = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert incident to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'severity': self.severity,
            'status': self.status,
            'priority': self.priority,
            'description': self.description,
            'assignee': self.assignee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def __repr__(self):
        return f'<Incident {self.id}: {self.title}>'

