# backend/app/services/integration_service.py

import logging
from typing import Any, Dict

# Import all integration classes you want to make available to the executor
from app.integrations.virusTotal_service import VirusTotalService
# from app.integrations.slack_service import SlackService # Placeholder for a future integration

logger = logging.getLogger(__name__)

class IntegrationService:
    """
    The Integration Dispatcher Service. 
    It acts as the single point of entry for the PlaybookExecutor 
    to route actions to any external security tool.
    """
    
    # Map integration names (used in playbook YAML/JSON) to their actual class reference
    SERVICE_MAP = {
        'virustotal': VirusTotalService,
        # 'slack': SlackService,
        # 'edr_tool': EDRService,
        # 'siem': SIEMService 
    }
    
    @classmethod
    def perform_action(cls, integration_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Finds the correct service class and executes the specified action method.
        
        Args:
            integration_name: The key from the SERVICE_MAP (e.g., 'virustotal').
            action: The static method name on the service class (e.g., 'query_ip_address').
            **kwargs: All parameters passed from the PlaybookExecutor (including the Alert object).
            
        Returns:
            The result dictionary from the integration module.
        """
        
        service_class = cls.SERVICE_MAP.get(integration_name.lower())
        
        if not service_class:
            logger.error(f"Attempted to call non-existent integration: {integration_name}")
            raise ValueError(f"Integration '{integration_name}' is not registered.")
            
        # Use Python's built-in getattr() to dynamically find the method name (action)
        action_method = getattr(service_class, action, None)
        
        if not action_method:
            logger.error(f"Action '{action}' not found on integration '{integration_name}'.")
            raise ValueError(f"Action '{action}' not defined for integration '{integration_name}'.")
            
        logger.info(f"Dispatching action: {integration_name}.{action} with data: {kwargs.keys()}")
            
        # Execute the method with all provided keyword arguments
        return action_method(**kwargs)