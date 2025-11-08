# backend/app/integrations/virustotal_service.py

import requests
import logging
from app.models.alert import Alert # Used for accessing alert data
from app.config import Config # Assuming you have a config module

logger = logging.getLogger(__name__)

# --- Configuration ---
# NOTE: Replace 'Config.VIRUSTOTAL_API_KEY' with your actual config loading method
# API Key should be read from .env (environment variables)
API_KEY = Config.VIRUSTOTAL_API_KEY 
BASE_URL = "https://www.virustotal.com/api/v3"

class VirusTotalService:
    """
    Integration module for interacting with the VirusTotal API.
    All public static methods here correspond to actions a playbook can call.
    """
    
    @staticmethod
    def _vt_request(endpoint, method="GET", data=None):
        """Internal helper to handle common request parameters and errors."""
        
        if not API_KEY:
            logger.error("VirusTotal API Key is not configured.")
            raise ConnectionError("VirusTotal API Key is missing.")

        headers = {
            "x-apikey": API_KEY,
            "Accept": "application/json"
        }
        url = f"{BASE_URL}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=15)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_code = e.response.status_code
            error_message = e.response.json().get('error', {}).get('message', 'Unknown VT error')
            logger.error(f"VirusTotal HTTP Error {error_code}: {error_message}")
            raise ConnectionError(f"VT API call failed: {error_message}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal Connection Error: {str(e)}")
            raise ConnectionError(f"VT connection failed: {str(e)}")

    @staticmethod
    def query_ip_address(ip_address: str, **kwargs) -> dict:
        """
        Action: Look up a specific IP address in VirusTotal.
        
        Args:
            ip_address: The IP address from the alert data.
            **kwargs: Includes the alert object, though not strictly needed here.
            
        Returns:
            A dictionary of relevant VT data.
        """
        logger.info(f"Querying VirusTotal for IP: {ip_address}")
        endpoint = f"/ip_addresses/{ip_address}"
        
        # This will raise an exception on failure, which the PlaybookExecutor will catch
        response_data = VirusTotalService._vt_request(endpoint)
        
        # We only return the relevant data the playbook needs
        attributes = response_data.get('data', {}).get('attributes', {})
        
        # Extract key metrics for a clean response
        analysis_stats = attributes.get('last_analysis_stats', {})
        
        result = {
            'status': 'success',
            'ip_address': ip_address,
            'owner_country': attributes.get('country'),
            'malicious_detections': analysis_stats.get('malicious', 0),
            'last_analysis_date': attributes.get('last_analysis_date'),
            'reputation': attributes.get('reputation'),
        }
        
        return result

    @staticmethod
    def query_file_hash(file_hash: str, **kwargs) -> dict:
        """
        Action: Look up a file hash (e.g., MD5, SHA256) in VirusTotal.
        """
        logger.info(f"Querying VirusTotal for hash: {file_hash}")
        # Hashes are queried using the /files endpoint
        endpoint = f"/files/{file_hash}"
        response_data = VirusTotalService._vt_request(endpoint)
        
        attributes = response_data.get('data', {}).get('attributes', {})
        
        return {
            'status': 'success',
            'hash': file_hash,
            'type': attributes.get('type_tag'),
            'size': attributes.get('size'),
            'malicious_detections': attributes.get('last_analysis_stats', {}).get('malicious', 0),
        }
        
# --- API Key Management Note ---
# The API Key should be stored in your .env file and loaded by a configuration
# system (e.g., Flask-Environments or a simple config class).
# Example Playbook Step to call this:
# {
#   "order": 1,
#   "action": "query_ip_address",
#   "integration": "virustotal",
#   "params": {"ip_address": "{{ alert.ip_address }}"} 
# }