from typing import TypedDict, Optional, Dict, Any, Union

class AgentState(TypedDict):
    """
    Represents the state of the healing agent workflow.
    """
    retry_count: int
    max_retries: int
    url: str
    error: Optional[str]
    plan: Optional[Dict[str, Any]]
    healing_result: Optional[Union[bool, Dict[str, Any]]]
    status: str  # 'running', 'success', 'failed', 'healing'
