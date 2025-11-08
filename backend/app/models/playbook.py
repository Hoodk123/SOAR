"""
Playbook Model - Automated response workflows
"""
from app.database.db import db
from datetime import datetime
import json


class Playbook(db.Model):
    """Security Playbook/Runbook Model"""
    
    __tablename__ = 'playbooks'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0')
    
    # Trigger Configuration
    trigger_condition = db.Column(db.Text)  # JSON or expression string
    auto_trigger = db.Column(db.Boolean, default=False)
    
    # Execution Steps (JSON array)
    steps = db.Column(db.Text, nullable=False)  # JSON string of steps
    
    # Configuration
    active = db.Column(db.Boolean, default=True, index=True)
    timeout_seconds = db.Column(db.Integer, default=300)
    retry_on_failure = db.Column(db.Boolean, default=True)
    max_retries = db.Column(db.Integer, default=3)
    
    # Classification
    category = db.Column(db.String(100))  # malware, phishing, network, etc.
    severity_requirement = db.Column(db.String(20))  # minimum severity to trigger
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed_at = db.Column(db.DateTime)
    
    # Metrics
    execution_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    avg_execution_time = db.Column(db.Float)  # seconds
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    execution_logs = db.relationship('ExecutionLog', back_populates='playbook', lazy='dynamic', cascade='all, delete-orphan')    
    def __repr__(self):
        return f'<Playbook {self.id}: {self.name} ({"Active" if self.active else "Inactive"})>'
    
    def to_dict(self):
        """Convert playbook to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'trigger_condition': self.trigger_condition,
            'auto_trigger': self.auto_trigger,
            'steps': json.loads(self.steps) if self.steps else [],
            'active': self.active,
            'timeout_seconds': self.timeout_seconds,
            'retry_on_failure': self.retry_on_failure,
            'max_retries': self.max_retries,
            'category': self.category,
            'severity_requirement': self.severity_requirement,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.get_success_rate(),
            'avg_execution_time': self.avg_execution_time,
            'created_by': self.created_by
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create playbook from dictionary"""
        steps = data.get('steps', [])
        if isinstance(steps, list):
            steps = json.dumps(steps)
        
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            version=data.get('version', '1.0'),
            trigger_condition=data.get('trigger_condition'),
            auto_trigger=data.get('auto_trigger', False),
            steps=steps,
            active=data.get('active', True),
            timeout_seconds=data.get('timeout_seconds', 300),
            retry_on_failure=data.get('retry_on_failure', True),
            max_retries=data.get('max_retries', 3),
            category=data.get('category'),
            severity_requirement=data.get('severity_requirement')
        )
    
    def get_steps(self):
        """Parse and return steps as list"""
        try:
            return json.loads(self.steps) if self.steps else []
        except json.JSONDecodeError:
            return []
    
    def add_step(self, step_data):
        """Add a new step to the playbook"""
        steps = self.get_steps()
        
        # Determine order
        max_order = max([s.get('order', 0) for s in steps], default=0)
        step_data['order'] = max_order + 1
        
        steps.append(step_data)
        self.steps = json.dumps(steps)
        self.updated_at = datetime.utcnow()
    
    def remove_step(self, step_order):
        """Remove a step by order number"""
        steps = self.get_steps()
        steps = [s for s in steps if s.get('order') != step_order]
        
        # Reorder remaining steps
        for idx, step in enumerate(sorted(steps, key=lambda x: x.get('order', 0)), start=1):
            step['order'] = idx
        
        self.steps = json.dumps(steps)
        self.updated_at = datetime.utcnow()
    
    def update_step(self, step_order, step_data):
        """Update an existing step"""
        steps = self.get_steps()
        for step in steps:
            if step.get('order') == step_order:
                step.update(step_data)
                break
        
        self.steps = json.dumps(steps)
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate the playbook"""
        self.active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the playbook"""
        self.active = False
        self.updated_at = datetime.utcnow()
    
    def record_execution(self, success, execution_time):
        """Record execution metrics"""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Update average execution time
        if self.avg_execution_time is None:
            self.avg_execution_time = execution_time
        else:
            self.avg_execution_time = (
                (self.avg_execution_time * (self.execution_count - 1) + execution_time) 
                / self.execution_count
            )
        
        self.last_executed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.execution_count == 0:
            return 0.0
        return round((self.success_count / self.execution_count) * 100, 2)
    
    def should_trigger_for_alert(self, alert):
        """Check if this playbook should trigger for given alert"""
        if not self.active or not self.auto_trigger:
            return False
        
        # Check severity requirement
        if self.severity_requirement:
            severity_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            alert_severity = severity_levels.get(alert.severity.lower(), 0)
            required_severity = severity_levels.get(self.severity_requirement.lower(), 0)
            
            if alert_severity < required_severity:
                return False
        
        # Evaluate trigger condition (basic implementation)
        if self.trigger_condition:
            try:
                # Simple condition evaluation (can be enhanced)
                condition = self.trigger_condition.lower()
                
                if 'source:' in condition:
                    source = condition.split('source:')[1].split()[0].strip()
                    if alert.source.lower() != source:
                        return False
                
                if 'severity:' in condition:
                    severity = condition.split('severity:')[1].split()[0].strip()
                    if alert.severity.lower() != severity:
                        return False
                
                return True
            except:
                return False
        
        return True
    
    def validate_steps(self):
        """Validate playbook steps structure"""
        steps = self.get_steps()
        
        if not steps:
            return False, "Playbook must have at least one step"
        
        # Check required fields
        for step in steps:
            if 'order' not in step:
                return False, "Each step must have an 'order' field"
            if 'action' not in step:
                return False, "Each step must have an 'action' field"
        
        # Check for duplicate orders
        orders = [s.get('order') for s in steps]
        if len(orders) != len(set(orders)):
            return False, "Duplicate step orders found"
        
        return True, "Validation passed"