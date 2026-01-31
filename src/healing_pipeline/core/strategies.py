from abc import ABC, abstractmethod
import time
from ..utils.logging import logger, log_healed_incident, log_hard_failure

class RecoveryStrategy(ABC):
    """Abstract base class for recovery strategies."""
    
    @abstractmethod
    def execute(self, context: dict):
        """Execute the recovery strategy."""
        pass

class RetryStrategy(RecoveryStrategy):
    """Implements exponential backoff retry logic."""
    
    def execute(self, context: dict):
        base_wait = float(context.get('wait_seconds', 1))
        retry_count = int(context.get('retry_count', 0))
        # Exponential backoff with simple cap
        wait_seconds = min(base_wait * (2 ** retry_count), 60)
        rationale = context.get('rationale', 'Retry initiated')
        logger.info(f"Strategy: RETRY | Wait: {wait_seconds}s | Rationale: {rationale} | retry_count: {retry_count}")
        time.sleep(wait_seconds)
        log_healed_incident("TaxDataIngestor", "RETRY", f"Waited {wait_seconds}s (retry {retry_count})")
        return True

class FailoverStrategy(RecoveryStrategy):
    """Switches to a backup API endpoint."""
    
    def execute(self, context: dict):
        rationale = context.get('rationale', 'Failover initiated')
        backup_url = context.get('failover_url')
        
        if not backup_url:
            logger.error("Failover requested but no backup URL provided in context.")
            return False
            
        logger.warning(f"Strategy: FAILOVER | Switch to: {backup_url} | Rationale: {rationale}")
        log_healed_incident("TaxDataIngestor", "FAILOVER", f"Switched to {backup_url}")
        return {"action": "update_url", "url": backup_url}

class EscalateStrategy(RecoveryStrategy):
    """Escalates the error and stops execution."""
    
    def execute(self, context: dict):
        rationale = context.get('rationale', 'Escalation initiated')
        logger.critical(f"Strategy: ESCALATE | Rationale: {rationale}")
        log_hard_failure("TaxDataIngestor", f"Escalated due to: {rationale}")
        raise SystemExit("Manual intervention required.")

class StrategyFactory:
    """Factory to get the appropriate strategy."""
    
    _strategies = {
        "RETRY": RetryStrategy,
        "FAILOVER": FailoverStrategy,
        "ESCALATE": EscalateStrategy
    }
    
    @classmethod
    def get_strategy(cls, action_name: str) -> RecoveryStrategy:
        # Handle cases where action contains multiple options (e.g., "RETRY | FAILOVER | ESCALATE")
        action_name = action_name.upper().strip()
        
        # If multiple options separated by |, pick the first one
        if "|" in action_name:
            actions = [a.strip() for a in action_name.split("|")]
            action_name = actions[0]  # Use first suggested action
        
        strategy_class = cls._strategies.get(action_name)
        if strategy_class:
            return strategy_class()
        raise ValueError(f"Unknown recovery strategy: {action_name}")
