from ..graph.state import AgentState
from ..core.worker import TaxDataIngestor
# Note: strategies.py can stay in core/strategies.py or move to graph/, sticking to core for now as per plan
from ..core.strategies import StrategyFactory
from overrides import override
from ..utils.logging import logger
from ..core.agent import AutomatedWatchdog # We will refactor this later, but need to import for now or use interfaces

# Ideally, we inject dependencies, but simple instantiation for now
def ingest_node(state: AgentState) -> AgentState:
    """
    Executes the data ingestion.
    """
    ingestor = TaxDataIngestor(state['url'])
    # Hack to sync simulation state if needed, or just let it fail naturally
    # For simulation consistency, we might need a persistent ingestor instance if the state is transient
    # But since this is a new node run, let's treat it as a fresh attempt unless we persist the worker object
    
    # IMPORTANT: The original worker has internal state `request_count` to simulate failure on 1st try.
    # If we recreate it every time, it will ALWAYS fail.
    # We need a way to persist the worker or pass request_count.
    # For this refactor, let's pass the attempt count from state to the worker or modify worker to accept it.
    
    # Updating worker.py might be needed to handle this statelessness better.
    # For now, let's rely on the worker's internal state if we can keep it alive, 
    # BUT LangGraph nodes are functions.
    
    # A cleaner way: Update worker to take specific config for simulation control
    # Or, we can store the ingestor in the state (not serializable usu. but works in memory)
    # Let's assume we can modify TaxDataIngestor to accept 'simulate_failure' flag based on retry_count.
    
    should_simulate_fail = (state['retry_count'] == 0)
    ingestor._simulate_failure = should_simulate_fail
    # We also need to set request_count to 1 if we want it to trigger the fail logic
    ingestor.request_count = 0 if should_simulate_fail else 1 

    try:
        result = ingestor.execute_ingestion() # This bumps request_count to 1
        return {"status": "success", "error": None}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return {"status": "failed", "error": str(e)}

def analyze_node(state: AgentState) -> AgentState:
    """
    Analyzes the error using the Watchdog (LangChain Agent).
    """
    watchdog = AutomatedWatchdog() # This will be the refactored LangChain version
    # Context needed for analysis
    context = {"url": state['url'], "retry_count": state['retry_count']}
    
    try:
        # We need to adapt analyze_error signature if we change it, assuming current sig for now
        # The refactored agent will return the plan dict directly
        plan = watchdog.analyze_error(Exception(state['error']), context) 
        return {"plan": plan, "status": "healing"}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Fallback plan
        return {"plan": {"action": "retry", "wait_seconds": 5, "rationale": "Analysis failed"}, "status": "healing"}

def heal_node(state: AgentState) -> AgentState:
    """
    Executes the healing plan.
    """
    plan = state['plan']
    # Execute strategy
    # StrategyFactory is in core/strategies.py
    
    # Mapping plan schema to strategy input
    # Plan keys: error_category, recovery_action (or action), wait_seconds, rationale
    action = plan.get('recovery_action') or plan.get('action') # handle potential schema mismatch
    if not action:
        logger.error("No action in plan")
        return {"healing_result": False, "status": "failed"}
        
    try:
        strategy = StrategyFactory.get_strategy(action)
        
        strategy_context = {
            "wait_seconds": plan.get('wait_seconds', 0),
            "rationale": plan.get('rationale'),
            "failover_url": settings.TAX_API_FAILOVER_URL if hasattr(settings, 'TAX_API_FAILOVER_URL') else "http://failover-api"
            # Note: Need to import settings
        }
        
        result = strategy.execute(strategy_context)
        
        # Check if strategy returned a URL update (e.g., Failover)
        state_update = {
            "healing_result": result, 
            "status": "healing_complete", 
            "retry_count": state['retry_count'] + 1
        }
        
        if isinstance(result, dict) and result.get("action") == "update_url":
            state_update["url"] = result["url"]
            
        return state_update
        
    except Exception as e:
        logger.error(f"Healing execution failed: {e}")
        return {"healing_result": False, "status": "failed"}

        return {"healing_result": False, "status": "failed"}

from ..config import settings
