"""
Utility Functions
Helper functions for common operations across the application
"""

def format_response(status, data=None, error=None):
    """Format API response consistently"""
    return {
        "status": status,
        "data": data,
        "error": error,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

def validate_city_name(city_name):
    """Validate city name input"""
    if not city_name or not isinstance(city_name, str):
        return False, "City name must be a non-empty string"
    if len(city_name) > 100:
        return False, "City name too long"
    return True, None

def safe_get_dict(d, *keys, default=None):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
    return d if d is not None else default
