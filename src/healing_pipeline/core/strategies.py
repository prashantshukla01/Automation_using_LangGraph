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
        wait_seconds = context.get('wait_seconds', 0)
        rationale = context.get('rationale', 'Retry initiated')
        logger.info(f"Strategy: RETRY | Wait: {wait_seconds}s | Rationale: {rationale}")
        time.sleep(wait_seconds)
        log_healed_incident("TaxDataIngestor", "RETRY", f"Waited {wait_seconds}s")
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
        strategy_class = cls._strategies.get(action_name.upper())
        if strategy_class:
            return strategy_class()
        raise ValueError(f"Unknown recovery strategy: {action_name}")
