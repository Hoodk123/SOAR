"""
Execution Log Model
Represents playbook execution logs
"""
from datetime import datetime
from app.database.db import db


class ExecutionLog(db.Model):
    """Execution log model for playbook runs"""
    
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    playbook_id = db.Column(db.Integer, db.ForeignKey('playbooks.id'), nullable=False)
    playbook = db.relationship('Playbook', back_populates='execution_logs', lazy=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=True)
    alert = db.relationship('Alert', back_populates='execution_logs', lazy=True)
    status = db.Column(db.String(50), nullable=False, default='pending', index=True)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    execution_data = db.Column(db.Text, nullable=True)  # JSON string
    
    def to_dict(self):
        """Convert execution log to dictionary"""
        return {
            'id': self.id,
            'playbook_id': self.playbook_id,
            'alert_id': self.alert_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'execution_data': self.execution_data
        }
    
    def __repr__(self):
        return f'<ExecutionLog {self.id}: playbook={self.playbook_id}, status={self.status}>'

