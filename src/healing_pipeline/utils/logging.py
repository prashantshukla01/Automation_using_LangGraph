import sys
from loguru import logger

def setup_logging(log_file: str = "recovery.log"):
    """Configure loguru logger."""
    logger.remove()  # Remove default handler

    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # Add file handler
    logger.add(
        log_file,
        rotation="10 MB",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

def log_healed_incident(component: str, strategy: str, details: str):
    """Log a successfully healed incident."""
    logger.success(f"HEALED | Component: {component} | Strategy: {strategy} | Details: {details}")

def log_hard_failure(component: str, error: str):
    """Log a hard failure that could not be recovered."""
    logger.critical(f"HARD FAILURE | Component: {component} | Error: {error}")
