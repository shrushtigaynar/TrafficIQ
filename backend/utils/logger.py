"""
Logging Configuration
Centralized logging setup for the application
"""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(__file__), '../../logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Log file paths
BACKEND_LOG = os.path.join(LOG_DIR, 'backend.log')
AGENT_LOG = os.path.join(LOG_DIR, 'agent.log')

# Create logger for backend
backend_logger = logging.getLogger('backend')
backend_logger.setLevel(logging.DEBUG)

# Create logger for agent
agent_logger = logging.getLogger('agent')
agent_logger.setLevel(logging.DEBUG)

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add file handlers
backend_handler = logging.FileHandler(BACKEND_LOG)
backend_handler.setFormatter(formatter)
backend_logger.addHandler(backend_handler)

agent_handler = logging.FileHandler(AGENT_LOG)
agent_handler.setFormatter(formatter)
agent_logger.addHandler(agent_handler)

# Add console handlers (for development)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
backend_logger.addHandler(console_handler)
agent_logger.addHandler(console_handler)

def get_backend_logger():
    """Get backend logger instance"""
    return backend_logger

def get_agent_logger():
    """Get agent logger instance"""
    return agent_logger
