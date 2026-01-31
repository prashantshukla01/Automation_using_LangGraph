from ..utils.logging import logger
from ..config import settings
from ..graph.workflow import create_healing_graph
from ..graph.state import AgentState

class PipelineEngine:
    def __init__(self, url: str = None, retries: int = None):
        self.base_url = url or settings.TAX_API_BASE_URL
        self.max_retries = retries if retries is not None else settings.MAX_RETRIES
        # Ingestor and Watchdog are now instantiated within nodes or passed via context
        self.graph = create_healing_graph()
        
    def run(self):
        logger.info(f"Starting Pipeline Engine with LangGraph | Max Retries: {self.max_retries}")
        
        # Initial State
        initial_state: AgentState = {
            "retry_count": 0,
            "max_retries": self.max_retries,
            "url": self.base_url,
            "error": None,
            "plan": None,
            "healing_result": None,
            "status": "running"
        }
        
        try:
            # Execute Graph
            result_state = self.graph.invoke(initial_state)
            
            # Check final status
            # If state has 'status' key, check it. 
            # Note: invoke returns the final state dict.
            
            final_status = result_state.get('status')
            
            if final_status == 'success':
                logger.success(f"Pipeline Completed Successfully.")
                return True
            else:
                logger.error(f"Pipeline Failed with status: {final_status}")
                return False
                
        except Exception as e:
            logger.critical(f"Graph Execution Error: {e}")
            return False
