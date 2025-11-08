# backend/app/utils/__init__.py

# --- 1. Expose Logging (security_logger is needed by alert_service.py) ---
from .logging_setup import security_logger, setup_logging

# --- 2. Expose Response Helpers (Needed by all routes) ---
from .response_helpers import build_response, build_error_response

# --- 3. Expose Validation Decorator/Functions (Needed by routes/services) ---
from .validators import (
    validate_required_fields,
    validate_severity,
    validate_status,
    validate_ip_address,
    validate_email,
    sanitize_string,
    validate_pagination,
    validate_json_field # Include all relevant ones
)

# --- 4. Expose the Missing Utility (Must be defined somewhere) ---
# NOTE: The next error will be here, as 'calculate_severity_score' 
# is referenced but not in your shared files.
# Assuming it is in a file called 'scoring_helpers.py' or 'helpers.py'.
# For now, let's assume you'll create a file called 'alert_scoring.py' in this folder.
# You will need to define this function in a new file next.
# from .alert_scoring import calculate_severity_score