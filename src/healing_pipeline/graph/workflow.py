from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import ingest_node, analyze_node, heal_node, enrich_node
from ..utils.logging import logger

def should_heal(state: AgentState):
    """Conditional edge: success -> end, fail -> analyze."""
    # If ingestion succeeded we proceed to enrichment (tax calc)
    if state['status'] == 'success':
        return "enrich"
    if state['retry_count'] >= state['max_retries']:
        return "end"
    return "analyze"

def should_retry(state: AgentState):
    """Conditional edge: after healing -> ingest (with update) or end (if failed)."""
    healing_result = state['healing_result']
    
    if healing_result is False:
        logger.critical("Healing failed or strategy escalated. Stop.")
        return "end"
    
    # If healing returned a dict (e.g. failover url), update state
    # BUT: Nodes only return State updates. 
    # The 'heal_node' returns partial state, merge happens automatically.
    # We need to process the result here or in the node.
    # Let's assume heal_node handled the logic and updated 'url' if needed.
    # Wait, heal_node implementation only returned healing_result object.
    # We might need a small post-processing step or handle it in heal_node.
    
    # Let's handle it in the node? 
    # Actually, let's look at what failover returns: {"action": "update_url", "url": ...}
    # We need to apply this to state['url'] before retrying. 
    # Ideally, heal_node should have done this. 
    # Let's fix heal_node to apply updates to state, OR do it here.
    # Doing it in node is cleaner. 
    
    return "ingest"

def create_healing_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("enrich", enrich_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("heal", heal_node)
    
    # Set Entry Point
    workflow.set_entry_point("ingest")
    
    # Add Edges
    workflow.add_conditional_edges(
        "ingest",
        should_heal,
        {
            "end": END,
            "analyze": "analyze",
            "enrich": "enrich"
        }
    )
    
    workflow.add_edge("analyze", "heal")

    # After enrichment, either finish (success) or analyze on validation failure
    def should_validate(state: AgentState):
        if state.get('status') == 'success':
            return 'end'
        return 'analyze'

    workflow.add_conditional_edges(
        "enrich",
        should_validate,
        {
            "end": END,
            "analyze": "analyze"
        }
    )
    
    workflow.add_conditional_edges(
        "heal",
        should_retry,
        {
            "end": END,
            "ingest": "ingest"
        }
    )
    
    return workflow.compile()
