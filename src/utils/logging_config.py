"""
Logging configuration for street coverage mapper.
"""
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set up handlers
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "processing.log")
    ]
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)