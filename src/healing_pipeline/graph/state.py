from typing import TypedDict, Optional, Dict, Any, Union

class AgentState(TypedDict):
    """Represents the complete state of the healing agent workflow."""
    retry_count: int
    max_retries: int
    url: str
    error: Optional[str]
    plan: Optional[Dict[str, Any]]
    healing_result: Optional[Union[bool, Dict[str, Any]]]
    status: str  # 'running', 'success', 'failed', 'healing', 'healing_complete'
    ingested_data: Optional[Any]  # Data from successful ingestion
    tax_result: Optional[Dict[str, Any]]  # Tax calculation result
