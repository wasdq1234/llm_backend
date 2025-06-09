"""Logging utilities"""

import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """Setup application logging"""
    
    log_level = level or ("DEBUG" if settings.debug else "INFO")
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langgraph").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name) 