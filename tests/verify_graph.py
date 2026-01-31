import sys
import os

# Ensure src is in path and prioritized
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from healing_pipeline.core.engine import PipelineEngine
import healing_pipeline
from healing_pipeline.utils.logging import logger

def verify():
    logger.info("Starting Verification...")
    
    # Initialize Engine with specific test URL if needed, or default
    # The default creates a worker that simulates failure on 1st try
    engine = PipelineEngine(retries=3)
    
    success = engine.run()
    
    if success:
        logger.success("Verification Passed: Pipeline healed and completed.")
    else:
        logger.error("Verification Failed.")

if __name__ == "__main__":
    verify()
