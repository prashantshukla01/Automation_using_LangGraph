"""Graph node functions for the healing pipeline."""
from ..config import settings
from ..core.agent import AutomatedWatchdog
from ..core.strategies import StrategyFactory
from ..core.worker import TaxDataIngestor
from ..graph.state import AgentState
from ..utils.logging import logger, log_healed_incident, log_hard_failure
from ..utils.tax_calculator import TaxCalculator

# Ideally, we inject dependencies, but simple instantiation for now
def ingest_node(state: AgentState) -> AgentState:
    """Ingest data from external API and handle transient failures."""
    ingestor = TaxDataIngestor(state['url'])

    # Control simulation of failures based on retry count
    # (first attempt triggers simulated 429, subsequent attempts succeed)
    should_simulate_fail = (state['retry_count'] == 0)
    ingestor._simulate_failure = should_simulate_fail
    ingestor.request_count = 0 if should_simulate_fail else 1

    try:
        result = ingestor.execute_ingestion()
        logger.info(f"Ingestion successful on attempt {state['retry_count'] + 1}")
        return {
            "status": "success",
            "error": None,
            "ingested_data": result.get('data') if isinstance(result, dict) else result
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return {"status": "failed", "error": str(e)}


def enrich_node(state: AgentState) -> AgentState:
    """
    Enriches ingested data by calculating tax via TaxJar and validating the result.
    On validation failure, the state will be marked as failed so the analyze/heal loop runs.
    """
    # Try to obtain an order payload from ingestion; fall back to a demo order for testing
    order = state.get('ingested_data')
    if not order or not isinstance(order, dict):
        # Demo order (same shape as tests/test_taxjar.py)
        order = {
          'from_country': 'US',
          'from_zip': '92093',
          'from_state': 'CA',
          'from_city': 'La Jolla',
          'from_street': '9500 Gilman Drive',
          'to_country': 'US',
          'to_zip': '90002',
          'to_state': 'CA',
          'to_city': 'Los Angeles',
          'to_street': '1335 E 103rd St',
          'amount': 15,
          'shipping': 1.5,
          'nexus_addresses': [
            {
              'id': 'Main Location',
              'country': 'US',
              'zip': '92093',
              'state': 'CA',
              'city': 'La Jolla',
              'street': '9500 Gilman Drive'
            }
          ],
          'line_items': [
            {
              'id': '1',
              'quantity': 1,
              'product_tax_code': '20010',
              'unit_price': 15,
              'discount': 0
            }
          ]
        }

    calculator = None
    try:
        calculator = TaxCalculator()
        tax_result = calculator.calculate_tax_for_order(order)
        logger.info("✓ TaxJar API call successful")
    except Exception as e:
        logger.warning(f"TaxJar API failed ({type(e).__name__}), using mock result")
        # Mock result for testing/offline scenarios
        tax_result = {
            'amount_to_collect': 1.46,
            'order_total_amount': 16.5,
            'has_nexus': True,
            'jurisdictions': []
        }

    # Helper to extract attribute or key
    def _get(obj, key):
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    amount_to_collect = _get(tax_result, 'amount_to_collect')
    order_total_amount = _get(tax_result, 'order_total_amount')

    # Basic validation: order total should match amount + shipping + collected tax
    expected_total = None
    try:
        expected_total = float(order.get('amount', 0)) + float(order.get('shipping', 0)) + float(amount_to_collect or 0)
    except Exception:
        expected_total = None

    valid = False
    if order_total_amount is not None and expected_total is not None:
        try:
            valid = abs(float(order_total_amount) - float(expected_total)) < 0.02
        except Exception:
            valid = False

    if valid:
        # Log successful validation and attach tax result
        log_healed_incident("TaxCalculator", "VALIDATION", f"Tax validated. Collected: ${amount_to_collect}, Total: ${order_total_amount}")
        return {"status": "success", "tax_result": tax_result, "healing_result": True}
    else:
        logger.error(f"Tax validation failed. expected=${expected_total} got=${order_total_amount}")
        # Attach tax_result for debugging and trigger analysis/heal
        return {"status": "failed", "error": "Tax validation failed", "tax_result": tax_result}


def analyze_node(state: AgentState) -> AgentState:
    """Analyze error and generate recovery plan using AI Watchdog."""
    watchdog = AutomatedWatchdog()
    context = {"url": state['url'], "retry_count": state['retry_count']}

    try:
        plan = watchdog.analyze_error(Exception(state['error']), context)
        logger.info(f"Recovery plan generated: {plan.get('recovery_action', 'unknown')}")
        return {"plan": plan, "status": "healing"}
    except Exception as e:
        logger.error(f"Analysis failed: {e}. Using fallback plan.")
        return {
            "plan": {"action": "retry", "wait_seconds": 1, "rationale": "Analysis failed, retry"},
            "status": "healing"
        }

def heal_node(state: AgentState) -> AgentState:
    """Execute recovery strategy based on the analysis plan."""
    plan = state['plan']
    action = plan.get('recovery_action') or plan.get('action')

    if not action:
        logger.error("No recovery action in plan")
        return {"healing_result": False, "status": "failed"}

    try:
        strategy = StrategyFactory.get_strategy(action)
        strategy_context = {
            "wait_seconds": plan.get('wait_seconds', 1),
            "rationale": plan.get('rationale'),
            "failover_url": getattr(settings, 'TAX_API_FAILOVER_URL', "http://failover-api"),
            "retry_count": state.get('retry_count', 0)
        }

        result = strategy.execute(strategy_context)
        state_update = {
            "healing_result": result,
            "status": "healing_complete",
            "retry_count": state['retry_count'] + 1
        }

        # Apply URL update if returned by failover strategy
        if isinstance(result, dict) and result.get("action") == "update_url":
            state_update["url"] = result["url"]

        return state_update

    except Exception as e:
        logger.error(f"Healing execution failed: {e}")
        return {"healing_result": False, "status": "failed"}

