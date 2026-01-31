# 🏥 Tax Compliance Automation Pipeline with Self-Healing

A resilient, agentic automation system for tax compliance that combines **LangGraph**, **LangChain**, and **TaxJar API**. Features autonomous error recovery with exponential backoff, AI-powered diagnosis, and multi-strategy healing.

## 📋 Overview

This pipeline automates tax compliance through:

1. **Data Ingestion** – Fetches order/transaction data from external APIs
2. **Tax Enrichment** – Calculates taxes using TaxJar's API
3. **Validation** – Verifies tax calculations meet compliance standards
4. **Self-Healing** – Automatically retries with exponential backoff on failures
5. **Logging** – Records successful validations and escalates critical issues

## 🎯 Key Features

- ✅ **Autonomous Healing Loop**: Detects failures, analyzes root causes, applies recovery strategies
- ✅ **Exponential Backoff Retries**: Intelligent retry timing (1s → 2s → 4s → 8s, capped at 60s)
- ✅ **AI-Powered Diagnosis**: Uses Gemini/OpenAI LLMs to analyze errors and generate plans
- ✅ **Tax Compliance**: Integrates TaxJar for accurate tax calculations and validation
- ✅ **Multiple Recovery Strategies**: RETRY, FAILOVER, ESCALATE
- ✅ **Structured Logging**: Detailed logs for debugging and compliance audits
- ✅ **Type-Safe State**: Uses TypedDict for predictable state management

## 🏗️ Architecture

### Pipeline Flow

```
Ingest (API Call)
    ↓
    ├─ SUCCESS → Enrich (Tax Calculation)
    │                ↓
    │                ├─ VALID → Log & Success
    │                └─ INVALID → Analyze (Diagnosis)
    │
    └─ FAILURE → Analyze (Diagnosis)
                     ↓
                Heal (Execute Strategy)
                     ↓
                    (Retry Ingest or Escalate)
```

### Graph Structure

The pipeline is modeled as a **LangGraph StateGraph** with conditional edges:

| Node | Purpose | Output |
|------|---------|--------|
| **ingest** | Fetch data from API; simulate/handle real failures | status, error, ingested_data |
| **enrich** | Calculate tax; validate amount | status, tax_result or error |
| **analyze** | Use AI Watchdog to diagnose error | plan (recovery action) |
| **heal** | Execute recovery strategy (retry, failover) | updated state, retry_count |

### State Schema (TypedDict)

```python
class AgentState(TypedDict):
    retry_count: int                      # Current retry attempt
    max_retries: int                      # Max allowed retries
    url: str                              # Current API endpoint
    error: Optional[str]                  # Last error message
    plan: Optional[Dict]                  # Recovery plan from AI
    healing_result: Optional[Union[bool, Dict]]  # Strategy result
    status: str                           # 'running', 'success', 'failed', 'healing', etc.
    ingested_data: Optional[Any]          # Data from successful ingest
    tax_result: Optional[Dict]            # Tax calculation result
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- API Keys (at least one of):
  - OpenAI: `OPENAI_API_KEY`
  - Gemini: `GEMINI_API_KEY`
  - TaxJar: `TAXJAR_API_KEY`

### Installation

```bash
# Clone and setup
cd /Users/prashantshukla/Desktop/automation_using_LangGraph
pip install -r requirements.txt
```

### Configuration

Create or update `.env`:

```env
# LLM API Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# API Endpoints
TAX_API_BASE_URL=https://jsonplaceholder.typicode.com
TAX_API_FAILOVER_URL=https://httpbin.org

# TaxJar Configuration (Sandbox)
TAXJAR_API_KEY=your_sandbox_key_here
TAXJAR_API_URL=https://api.sandbox.taxjar.com

# Model & Retries
LLM_MODEL=gpt-4-turbo
MAX_RETRIES=3
```

### Running the Pipeline

#### Option 1: Using the CLI

```bash
python -m healing_pipeline.cli --retries 3 --log-file recovery.log
```

#### Option 2: Using the Structured Runner (Recommended)

```bash
python -c "from src.healing_pipeline.pipeline_runner import main; main()"
```

Or:

```bash
cd src
python -m healing_pipeline.pipeline_runner
```

## 📊 Pipeline Behavior & Example Output

### Scenario: Transient API Failure

**Execution Flow:**

1. **Attempt 1 (Ingest)**
   - API returns 429 (Rate Limit)
   - Status: FAILED

2. **Diagnose**
   - Watchdog analyzes: "Rate limit error detected"
   - Recovery Action: RETRY with wait
   - Plan: `{"recovery_action": "RETRY", "wait_seconds": 2}`

3. **Heal**
   - Exponential backoff: wait 2 × 2^0 = 2 seconds
   - Increment retry_count to 1

4. **Attempt 2 (Ingest)**
   - API call succeeds
   - Returns order data

5. **Enrich (Tax Calculation)**
   - TaxCalculator calls TaxJar API
   - Result: `{ "amount_to_collect": 1.46, "order_total_amount": 16.5, ... }`
   - Validation: amount + shipping + tax ≈ total ✓

6. **Result**
   - Log: "HEALED | Component: TaxCalculator | Strategy: VALIDATION | Details: Tax validated..."
   - Status: SUCCESS

### Example Logs

```
2026-01-31 10:15:32 | INFO | healing_pipeline.core.engine:run:32 - Starting Pipeline Engine with LangGraph | Max Retries: 3
2026-01-31 10:15:33 | ERROR | healing_pipeline.core.worker:execute_ingestion:27 - Ingestion failed: 429 Client Error: Too Many Requests
2026-01-31 10:15:33 | INFO | healing_pipeline.core.agent:analyze_error:59 - Watchdog activated. Analyzing error: 429 Client Error
2026-01-31 10:15:34 | INFO | healing_pipeline.core.agent:analyze_error:61 - Gemini Watchdog Plan: {'error_category': 'Rate Limit Exceeded', 'recovery_action': 'RETRY', 'wait_seconds': 2, 'rationale': 'Standard rate limit handling'}
2026-01-31 10:15:34 | INFO | healing_pipeline.core.strategies:execute:25 - Strategy: RETRY | Wait: 2.0s | Rationale: Standard rate limit handling | retry_count: 0
2026-01-31 10:15:36 | SUCCESS | healing_pipeline.utils.logging:log_healed_incident:31 - HEALED | Component: TaxDataIngestor | Strategy: RETRY | Details: Waited 2.0s (retry 0)
2026-01-31 10:15:37 | INFO | healing_pipeline.graph.nodes:ingest_node:23 - Ingestion successful on attempt 1
2026-01-31 10:15:37 | INFO | healing_pipeline.graph.nodes:enrich_node:97 - TaxCalculator initialized
2026-01-31 10:15:38 | SUCCESS | healing_pipeline.utils.logging:log_healed_incident:31 - HEALED | Component: TaxCalculator | Strategy: VALIDATION | Details: Tax validated for order. Collected: 1.46
2026-01-31 10:15:38 | INFO | healing_pipeline.core.engine:run:52 - Pipeline Completed Successfully.
```

## 🔄 Recovery Strategies

### RETRY (Exponential Backoff)

- **Formula**: `wait = min(base_wait × 2^retry_count, 60)`
- **Example**: 1s, 2s, 4s, 8s, 16s, 32s, 60s (capped)
- **Use Case**: Transient failures (rate limits, network blips)

### FAILOVER

- **Action**: Switch to alternate API endpoint
- **Example**: Primary down → Use `TAX_API_FAILOVER_URL`
- **Use Case**: Service degradation, regional outages

### ESCALATE

- **Action**: Stop pipeline and require manual intervention
- **Use Case**: Unrecoverable errors, auth failures, data validation errors

## 🧪 Testing

### Unit Tests (Mocked TaxJar)

```bash
pytest tests/ -v
```

### Integration Test (Real Sandbox TaxJar)

```bash
pytest tests/test_taxjar.py -v
```

### Manual Pipeline Test

```bash
python -c "from src.healing_pipeline.pipeline_runner import main; main()"
```

## 📁 Project Structure

```
src/healing_pipeline/
├── pipeline_runner.py      # Structured runner with visualization
├── cli.py                  # CLI entry point
├── config.py               # Configuration management (Pydantic)
├── core/
│   ├── agent.py            # AI Watchdog (LangChain + Gemini)
│   ├── engine.py           # Pipeline execution engine
│   ├── strategies.py       # Recovery strategies (RETRY, FAILOVER, ESCALATE)
│   └── worker.py           # Data ingestion worker (TaxDataIngestor)
├── graph/
│   ├── nodes.py            # Graph nodes: ingest, enrich, analyze, heal
│   ├── state.py            # TypedDict for AgentState
│   └── workflow.py         # LangGraph StateGraph definition
└── utils/
    ├── logging.py          # Structured logging with loguru
    └── tax_calculator.py   # TaxJar API wrapper
```

## 🔐 Security & Best Practices

- ✅ Never commit `.env` files; use environment variables in production
- ✅ Use sandbox TaxJar credentials in CI/CD
- ✅ Rotate API keys regularly
- ✅ Monitor logs for repeated failures (potential attacks)
- ✅ Validate all external inputs before processing

## 🐛 Troubleshooting

### "TAXJAR_API_KEY is not set"

→ Add `TAXJAR_API_KEY` to `.env` or environment variables

### "Gemini API Key not provided, running in MOCK MODE"

→ This is fine! The pipeline will use a mock plan. For real AI diagnostics, set `GEMINI_API_KEY`

### "Max retries exceeded"

→ Check logs for the root cause. Common issues:
- Network connectivity
- API authentication (wrong key)
- Rate limiting on external service
- TaxJar sandbox quotas

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [TaxJar API Docs](https://developers.taxjar.com/)
- [Exponential Backoff Strategy](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

## 📝 License

MIT License – See LICENSE file for details

---

**Last Updated**: 31 January 2026  
**Version**: 1.0.0
