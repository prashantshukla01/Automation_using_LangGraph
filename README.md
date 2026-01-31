# 🔄 Self-Healing Automation Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-00a96f)](https://langchain-ai.github.io/langgraph/)
[![Ollama Integration](https://img.shields.io/badge/Ollama-gemma3:1b-fa8231)](https://ollama.ai)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, resilient automation system that autonomously recovers from transient failures and API instabilities. Built with **LangGraph**, **LangChain**, and **Ollama**, this pipeline implements autonomous healing using AI-powered error analysis and exponential backoff recovery strategies.

---

## ✨ Key Features

- **🤖 AI-Powered Self-Healing** — Uses local LLM (Ollama gemma3:1b) to diagnose errors and generate intelligent recovery plans
- **📊 State Machine Architecture** — LangGraph-based StateGraph for deterministic, observable execution
- **⏱️ Exponential Backoff** — Smart retry mechanism: 2s → 4s → 8s → 16s → 32s → 60s (capped)
- **🔀 Multi-Strategy Recovery** — RETRY, FAILOVER, and ESCALATE strategies for different failure types
- **💰 Tax Compliance Automation** — TaxJar API integration with validation and fallback support
- **📝 Comprehensive Logging** — Structured logging with file rotation and colored console output
- **🔌 Local LLM Support** — Runs on local Ollama (no API keys, no cloud dependency)

---

## 🏗️ Architecture Overview

### Graph-Based Flow (LangGraph StateGraph)

```
┌─────────────┐
│ START       │
└──────┬──────┘
       │
       ▼
┌──────────────────┐         ┌──────────────┐
│ 1. INGEST NODE   │──FAIL──→│ 2. ANALYZE   │
│ (API Data Fetch) │         │ (AI Watchdog)│
└────────┬─────────┘         └──────┬───────┘
         │ SUCCESS                  │
         ▼                          ▼
┌──────────────────┐         ┌──────────────┐
│ 3. ENRICH NODE   │         │ 4. HEAL NODE │
│ (Tax Calc        │         │ (Strategy)   │
│  Validation)     │         │              │
└────────┬─────────┘         └──────┬───────┘
         │                          │
      ✓/✗                          │
         │◄─────────────────────────┘
         │
    ┌────┴─────┐
    │           │
   ✅          ⚠️
 SUCCESS     MAX_RETRIES
  (Logged)   (Escalate)
```

### Workflow Stages

| Stage | Component | Purpose |
|-------|-----------|---------|
| **1. Ingest** | `ingest_node` | Fetch data from external APIs, detect failures |
| **2. Analyze** | `analyze_node` + AI Watchdog | Diagnose errors using LLM, generate recovery plan |
| **3. Enrich** | `enrich_node` | Calculate taxes, validate results against expectations |
| **4. Heal** | `heal_node` | Execute recovery strategy based on analysis |
| **Loop** | `should_retry()` | Decide: retry, escalate, or terminate |

### Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **ingest_node** | Fetch data from external API with simulated failures | ✅ Operational |
| **enrich_node** | Calculate taxes via TaxJar, validate results | ✅ Operational |
| **analyze_node** | AI-powered error diagnosis via Ollama | ✅ Operational |
| **heal_node** | Execute recovery strategies (RETRY/FAILOVER/ESCALATE) | ✅ Operational |
| **RetryStrategy** | Exponential backoff: 2→4→8→16→32→60s | ✅ Verified |
| **FailoverStrategy** | Switch to alternate API endpoint | ✅ Available |
| **EscalateStrategy** | Trigger manual intervention | ✅ Available |
| **Watchdog (AI Agent)** | LLM-based error analysis via Ollama gemma3:1b | ✅ Operational |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** (with gemma3:1b model)
- **pip** or **conda** for package management

### Installation & Setup

#### 1️⃣ Install Ollama & Pull Model

```bash
# Install Ollama from https://ollama.ai
# Then pull the gemma3:1b model (815 MB)
ollama pull gemma3:1b

# Verify it's available
ollama list
# Expected output:
# gemma3:1b    815 MB    8648f39daa8f
```

#### 2️⃣ Start Ollama Service

```bash
# Start Ollama (runs on http://localhost:11434 by default)
ollama serve

# In another terminal, verify it's running:
curl http://localhost:11434/api/tags
```

#### 3️⃣ Clone & Setup Project

```bash
# Clone repository
git clone https://github.com/yourusername/automation_using_LangGraph.git
cd automation_using_LangGraph

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment

Create/update `.env` file:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b

# Tax API Configuration (Optional)
TAXJAR_API_KEY=your_taxjar_key_here
TAX_API_BASE_URL=https://api.sandbox.taxjar.com
TAX_API_FAILOVER_URL=https://api-backup.example.com

# Pipeline Configuration
MAX_RETRIES=3
LOG_LEVEL=INFO
```

#### 5️⃣ Run the Pipeline

```bash
# Simple run
python src/healing_pipeline/pipeline_runner.py

# With logging output
python src/healing_pipeline/pipeline_runner.py 2>&1 | tee execution_$(date +%s).log

# Watch logs in real-time
tail -f pipeline_execution.log
```

---

## 📖 Usage Guide

### Running the Pipeline

### Command-Line Options

```bash
# Run with custom retry count
python src/healing_pipeline/pipeline_runner.py --retries 5

# Run with custom log level
python src/healing_pipeline/pipeline_runner.py --log-level DEBUG

# Run with custom API endpoint
python src/healing_pipeline/pipeline_runner.py --url https://custom-api.example.com
```

### Docker Execution (Optional)

```bash
# Build Docker image
docker build -t healing-pipeline:latest .

# Run container with Ollama (host network mode)
docker run --network host --env-file .env healing-pipeline:latest
```

---

## 🧪 Development

### Project Structure

```
src/healing_pipeline/
├── cli.py                  # CLI entry point
├── config.py              # Pydantic configuration management
├── pipeline_runner.py     # Main pipeline orchestrator
│
├── core/                  # Core business logic
│   ├── agent.py           # AI Watchdog (LLM-based error analysis)
│   ├── engine.py          # Pipeline execution engine
│   ├── strategies.py      # Recovery strategies (RETRY, FAILOVER, ESCALATE)
│   └── worker.py          # Data ingestion worker
│
├── graph/                 # LangGraph workflow
│   ├── nodes.py           # Graph nodes (ingest, enrich, analyze, heal)
│   ├── state.py           # TypedDict for graph state management
│   └── workflow.py        # Graph topology and edge definitions
│
└── utils/                 # Utilities
    ├── logging.py         # Structured logging with loguru
    └── tax_calculator.py  # Tax calculation helpers

tests/
├── test_taxjar.py         # TaxJar API tests
└── verify_graph.py        # Graph workflow verification
```

### How It Works

#### 1. **Ingest Node** (`ingest_node`)
- Fetches data from external API
- Simulates 429 rate limit error on first attempt
- Succeeds on retry (demonstrates recovery)

#### 2. **Enrich Node** (`enrich_node`)
- Calls TaxJar API to calculate taxes
- Validates result against expected values
- Falls back to mock data if API unavailable

#### 3. **Analyze Node** (`analyze_node`)
- Invokes AI Watchdog when error occurs
- Sends error context to Ollama gemma3:1b
- Receives structured recovery plan (JSON)

#### 4. **Heal Node** (`heal_node`)
- Executes recovery strategy from plan
- Applies exponential backoff for retries
- Updates pipeline state

#### 5. **State Management**

The pipeline maintains `AgentState` (TypedDict) with:
- `retry_count`: Current retry attempt number
- `max_retries`: Maximum allowed retries (default: 3)
- `url`: Target API endpoint
- `error`: Last error message
- `plan`: AI-generated recovery plan
- `status`: Pipeline status (running/success/failed)
- `ingested_data`: Retrieved API data
- `tax_result`: Tax calculation result
- And more...

### Recovery Strategies

#### **RetryStrategy** — Exponential Backoff
```
Retry 0: wait = min(2 × 2^0, 60) = 2s
Retry 1: wait = min(2 × 2^1, 60) = 4s
Retry 2: wait = min(2 × 2^2, 60) = 8s
...
Retry 5+: wait = min(2 × 2^5, 60) = 60s (capped)
```

#### **FailoverStrategy** — Endpoint Switching
- Switches to backup API endpoint
- Updates state with new URL
- Resumes from current position

#### **EscalateStrategy** — Manual Intervention
- Logs critical error
- Triggers alert/notification
- Awaits manual resolution

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_taxjar.py -v

# Run with coverage report
pytest tests/ --cov=src/healing_pipeline --cov-report=html
```

### Logging

The system uses **loguru** for structured logging:

```bash
# Check execution logs
tail -f pipeline_execution.log

# Check recovery logs
tail -f recovery.log

# View formatted logs (colored, timestamped)
cat pipeline_execution.log | grep "SUCCESS\|ERROR\|CRITICAL"
```

**Log Levels:**
- `DEBUG` — Detailed execution flow
- `INFO` — Pipeline milestones
- `SUCCESS` — Successful recovery
- `WARNING` — Potential issues
- `ERROR` — Recoverable errors
- `CRITICAL` — Pipeline failures

---

## 🔬 Understanding the Exponential Backoff

The exponential backoff formula prevents overwhelming a struggling API while ensuring responsive recovery:

```python
# Formula: wait = min(base_wait × 2^retry_count, MAX_WAIT_SECONDS)
base_wait = 2  # Start with 2 seconds
max_wait = 60  # Cap at 60 seconds

retry_0: 2s   ← Fast initial retry for transient errors
retry_1: 4s   ← Gradual increase
retry_2: 8s
retry_3: 16s
retry_4: 32s  ← Gives server time to recover
retry_5+: 60s ← Maximum wait (prevents infinite growth)
```

**Benefits:**
- ✅ Recovers quickly from transient failures
- ✅ Gradually backs off to avoid hammering struggling APIs
- ✅ Capped maximum prevents forever waits
- ✅ Proven effective in production systems (AWS, GCP)

---

## 🤖 AI Watchdog (Ollama Integration)

The pipeline uses **Ollama's gemma3:1b** (local, lightweight) for error analysis:

```python
# Example: Error occurs → AI analyzes → Recovery plan generated

Error: "429 Client Error: Too Many Requests"
  ↓
Ollama Analysis (gemma3:1b):
  "The client is exceeding the rate limit. 
   Implementing exponential backoff retry mechanism."
  ↓
Generated Plan:
{
  "error_category": "Rate Limit",
  "recovery_action": "RETRY",
  "wait_seconds": 2,
  "rationale": "Server busy, backing off"
}
  ↓
Strategy Executed: Wait 2s, then retry
```

**Why Ollama?**
- 🔒 Privacy — Runs locally, no API keys needed
- ⚡ Fast — No network roundtrips
- 💰 Free — No API costs
- 🤏 Lightweight — 815 MB model
- 🔌 Extensible — Easy to swap models (llama2, mistral, etc.)


## 🔧 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags | python -m json.tool

# If not, start it
ollama serve

# Verify gemma3:1b is loaded
ollama list
```

### Model Loading Issues

```bash
# Pull the model explicitly
ollama pull gemma3:1b

# Check model size (should be ~815 MB)
du -h ~/.ollama/models/manifests/registry.ollama.ai/library/gemma3/1b/

# Verify import
python -c "from langchain_ollama import ChatOllama; print('✓ OK')"
```

### Pipeline Recursion Limit

If you see `GRAPH_RECURSION_LIMIT` error:

```bash
# Increase max_retries in .env or config.py
MAX_RETRIES=5  # Default is 3

# Or check tax validation logic (see enrich_node in nodes.py)
```

### Tax API Failures

```bash
# Check TaxJar credentials
grep TAXJAR .env

# Verify API endpoint is accessible
curl -H "Authorization: Bearer $TAXJAR_API_KEY" \
  https://api.sandbox.taxjar.com/v2/categories

# Check logs for mock fallback
grep "using mock result" pipeline_execution.log
```

---

## 📊 Performance & Metrics

### Typical Execution Flow

```
Total Runtime: ~2 minutes (with exponential backoff)

Breakdown:
├─ Initial ingestion attempt: ~0s
├─ Rate limit error detected: ~0s
├─ Ollama analysis: ~1-2s
├─ Recovery cycle 1 (2s wait + retry): ~3s
├─ Recovery cycle 2 (4s wait + retry): ~5s
├─ Recovery cycle 3 (8s wait + retry): ~9s
├─ Recovery cycle 4 (16s wait + retry): ~17s
├─ Recovery cycle 5 (32s wait + retry): ~33s
├─ Recovery cycle 6 (60s wait + retry): ~61s
└─ Total: ~130s (2+ minutes)
```

### Resource Usage

- **Ollama Memory**: ~1-2 GB (for gemma3:1b)
- **Python Process**: ~100-150 MB
- **Disk Space**: ~815 MB (model) + logs
- **Network**: Minimal (local Ollama, no cloud calls)

---

## 📋 Best Practices

### ✅ Do's

- ✅ Run Ollama in background: `nohup ollama serve > ollama.log 2>&1 &`
- ✅ Monitor logs regularly: `tail -f pipeline_execution.log`
- ✅ Use `.env` for sensitive configuration (API keys)
- ✅ Test with `--log-level DEBUG` during development
- ✅ Set `MAX_RETRIES` based on SLA requirements
- ✅ Implement custom strategies for specialized failures

### ❌ Don'ts

- ❌ Don't expose `.env` file in version control
- ❌ Don't set `MAX_RETRIES` too high (avoid runaway processes)
- ❌ Don't run multiple pipelines on same Ollama (resource contention)
- ❌ Don't ignore CRITICAL level logs
- ❌ Don't modify state directly in nodes (breaks reproducibility)

---

## 🚀 Advanced Configuration

### Custom LLM Model

Replace gemma3:1b with any Ollama-supported model:

```bash
# Pull different model
ollama pull llama2
ollama pull mistral
ollama pull neural-chat

# Update .env
OLLAMA_MODEL=mistral
```

### Custom Recovery Strategies

Extend the strategy system:

```python
# In src/healing_pipeline/core/strategies.py

class CustomStrategy(RecoveryStrategy):
    def execute(self, context: dict) -> dict:
        # Your custom logic here
        return {"executed": True, "details": "Custom action performed"}

# Register in StrategyFactory
StrategyFactory._strategies["CUSTOM"] = CustomStrategy
```

### Parallel Pipeline Execution

Run multiple independent pipelines:

```bash
# Terminal 1
python src/healing_pipeline/pipeline_runner.py --url endpoint1

# Terminal 2
python src/healing_pipeline/pipeline_runner.py --url endpoint2

# Check logs
tail -f recovery.log
```

---

## 📚 Related Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Models](https://ollama.ai/library)
- [LangChain Agents](https://python.langchain.com/docs/agents/)
- [TaxJar API Docs](https://developers.taxjar.com/)
- [Exponential Backoff Best Practices](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linter and formatter
black src/ tests/
flake8 src/ tests/

# Run type checking
mypy src/

# Run tests
pytest tests/ -v --cov
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- 📧 **Issues**: Open a GitHub issue for bugs and feature requests
- 💬 **Discussions**: Use GitHub Discussions for questions and ideas
- 📖 **Documentation**: Check docs/ folder for detailed guides

---

**Made with ❤️ for resilient, autonomous systems**
