from functools import wraps
from flask import request, jsonify
import time
from datetime import datetime

def rate_limit(requests_per_minute=10, window_size=60):
    """Rate limiting decorator"""
    requests = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            now = time.time()
            
            # Remove requests outside the window
            requests[:] = [req for req in requests if now - req < window_size]
            
            if len(requests) >= requests_per_minute:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            requests.append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        return timestamp
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_severity_color(severity):
    """Get Bootstrap color class for severity"""
    colors = {
        'CRITICAL': 'danger',
        'HIGH': 'warning',
        'MEDIUM': 'info',
        'LOW': 'secondary',
        'INFO': 'primary'
    }
    return colors.get(severity, 'secondary')