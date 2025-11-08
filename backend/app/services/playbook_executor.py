# backend/app/services/playbook_executor.py

import logging
from datetime import datetime
import time # Used for calculating execution time

from app.database.db import db
from app.models.alert import Alert # Assumes Alert model is ready
from app.models.playbook import Playbook
from app.models.execution_log import ExecutionLog # Assumes ExecutionLog model is ready

# IMPORT THE NEXT LAYER: The Integration Service
# This service acts as a router to all your external tool connectors
from app.services.integration_service import IntegrationService # We will create this next!

logger = logging.getLogger(__name__)

class PlaybookExecutor:
    """
    Core service responsible for initiating and managing playbook execution.
    This service orchestrates steps defined in the Playbook model.
    """

    @staticmethod
    def execute(playbook_id, alert_id):
        """
        Executes a playbook synchronously (e.g., when manually triggered).
        This method contains the main automation logic.
        """
        start_time = time.time()
        
        # 1. Fetch required data
        alert = Alert.query.get(alert_id)
        playbook = Playbook.query.get(playbook_id)
        
        if not alert or not playbook:
            logger.error(f"Execution failed: Alert ({alert_id}) or Playbook ({playbook_id}) not found.")
            return False
            
        logger.info(f"Starting execution of Playbook '{playbook.name}' for Alert {alert.id}")
        
        # 2. Create Execution Log
        log = ExecutionLog(
            playbook_id=playbook.id, 
            alert_id=alert.id, 
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Initialize execution state
        success = True
        
        # 3. Iterate and Execute Steps
        steps = playbook.get_steps() # Uses the get_steps() method from the Playbook model
        
        # Steps are typically sorted by the 'order' field defined in the model
        for step in sorted(steps, key=lambda s: s.get('order', 0)):
            step_order = step.get('order', 0)
            
            try:
                logger.info(f"  -> Step {step_order}: Executing action '{step['action']}'")
                
                # This function connects the PlaybookExecutor to the Integrations layer
                result = PlaybookExecutor._dispatch_action(step, alert)
                
                # Check for action failure (e.g., API call failed)
                if result.get('status') == 'failed':
                    raise RuntimeError(f"Action failed: {result.get('message', 'Unknown integration error')}")
                
                logger.info(f"  -> Step {step_order} completed successfully.")
                
            except Exception as e:
                logger.error(f"  -> Step {step_order} FAILED: {str(e)}")
                log.status = 'failed'
                log.error_message = f"Step {step_order} failed: {str(e)}"
                success = False
                
                # Stop execution if a step fails
                break 

        # 4. Finalize Execution
        end_time = time.time()
        execution_duration = end_time - start_time
        
        if success:
            log.status = 'completed'
        
        log.completed_at = datetime.utcnow()
        db.session.commit()
        
        # 5. Update Playbook metrics
        playbook.record_execution(success, execution_duration) # Uses the method from the Playbook model
        db.session.commit()
        
        logger.info(f"Playbook execution finished in {execution_duration:.2f} seconds. Status: {log.status}")
        return success

    @staticmethod
    def execute_async(playbook_id, alert_id):
        """
        Initiates playbook execution in the background.
        In a production SOAR, this would queue the task using a tool like Celery or Redis Queue.
        
        For initial development, we'll execute synchronously to test the flow.
        """
        logger.info(f"Async simulation: Queuing playbook {playbook_id} for alert {alert_id}")
        
        # --- FUTURE DEVELOPMENT HOOK ---
        # import celery_app
        # celery_app.send_task('playbook_executor_task', args=[playbook_id, alert_id])
        # -------------------------------
        
        # Synchronous execution for now
        return PlaybookExecutor.execute(playbook_id, alert_id)

    @staticmethod
    def _dispatch_action(step: dict, alert: Alert):
        """
        Internal method to route a playbook step to the correct Integration Service.
        
        Expected Step Format (Example):
        {
            "order": 1,
            "action": "isolate_host",
            "integration": "edr_service",
            "params": {
                "ip": alert.ip_address,
                "reason": "malware_detected"
            }
        }
        """
        integration_name = step.get('integration')
        action_name = step.get('action')
        params = step.get('params', {})
        
        # Pass the alert object itself in case the integration needs more than just parameters
        params['alert'] = alert 
        
        if not integration_name:
            return {'status': 'failed', 'message': "Playbook step missing 'integration' field."}

        # The IntegrationService routes the call to the correct module (e.g., EDRService, VirustotalService)
        # This design keeps the PlaybookExecutor clean and integration-agnostic.
        try:
            result = IntegrationService.perform_action(integration_name, action_name, **params)
            return {'status': 'success', 'data': result}
        except Exception as e:
            logger.error(f"Integration call to {integration_name}.{action_name} failed: {str(e)}")
            return {'status': 'failed', 'message': str(e)}