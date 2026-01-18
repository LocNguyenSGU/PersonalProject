import logging
import json
import traceback
from datetime import datetime
from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception details if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)


def setup_logger(name: str) -> logging.Logger:
    """Setup a logger with JSON formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(handler)
    
    return logger


logger = setup_logger(__name__)
