# Self-Healing Automation Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A resilient, agentic automation system designed to handle transient failures and API instabilities autonomously. Built with **LangGraph** and **LangChain**, this pipeline implements a "Human-in-the-Loop" style autonomous healing process, where an AI Watchdog analyzes errors and prescribes recovery strategies on the fly.

## 🚀 Key Features

*   **Resilient Data Ingestion**: Robust ingestion layer capable of handling diverse data sources and simulating failures for testing.
*   **AI-Powered Error Analysis**: Leverages LLMs (via LangChain's Agent Framework) to intelligently diagnose runtime exceptions and generate actionable recovery plans.
*   **Graph-Based Execution Loop**: Utilizes **LangGraph** to model the pipeline as a state machine (`Ingest` -> `Analyze` -> `Heal` -> `Retry`), ensuring deterministic and observable execution flows.
*   **Modular Recovery Strategies**: Extensible strategy system supporting various healing actions like dynamic waits, failover routing, and refined retries.
*   **Self-Correction**: Automatically updates pipeline state (e.g., switching API endpoints) based on successful healing outcomes.

## 🏗️ Architecture

The system is architected as a cyclic graph:

1.  **Ingest Node**: Attempts to fetch or process data. If successful, the workflow ends.
2.  **Failure Detection**: On exception, the workflow transitions to the analysis phase instead of crashing.
3.  **Analyze Node**: An AI Agent examines the error logs and context. It produces a structured **Recovery Plan**.
4.  **Heal Node**: Executes the specific strategy defined in the plan (e.g., "Switch to Backup URL").
5.  **Retry Loop**: The workflow loops back to ingestion with the patched state.

## 🛠️ Getting Started

### Prerequisites

*   Python 3.10 or higher
*   Docker (optional, for containerized execution)
*   API Key for OpenAI or Gemini (for the AI Watchdog)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/healing-pipeline.git
    cd healing-pipeline
    ```

2.  **Set up the environment**:
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_openai_key_here
    # OR
    GEMINI_API_KEY=your_gemini_key_here
    
    TAX_API_BASE_URL=https://api.example.com/v1
    TAX_API_FAILOVER_URL=https://backup-api.example.com/v1
    ```

3.  **Install dependencies**:
    ```bash
    make setup
    ```

### ▶️ Usage

#### Running Locally

To run the pipeline with the default configuration:

```bash
make run
```

Or use the CLI directly for more control:

```bash
healing-run --url "https://api.custom-endpoint.com" --retries 5
```

**CLI Options:**
*   `--url`: Override the target API base URL.
*   `--retries`: Set the maximum number of self-healing attempts.
*   `--log-file`: Path to the log file (default: `recovery.log`).

#### Running with Docker

Build and run the containerized application:

```bash
make docker-build
docker run --env-file .env healing-pipeline
```

#### Cleaning Up

To clean up temporary files and caches:

```bash
make clean
```

## 🧪 Development

### Project Structure

```
src/healing_pipeline/
├── cli.py              # Entry point for the CLI
├── config.py           # Configuration management using Pydantic
├── core/               # Core business logic
│   ├── agent.py        # AI Watchdog implementation
│   ├── engine.py       # Pipeline execution engine
│   ├── strategies.py   # Recovery strategy implementations
│   └── worker.py       # Data ingestion worker
├── graph/              # LangGraph definitions
│   ├── nodes.py        # Graph nodes (Ingest, Analyze, Heal)
│   ├── state.py        # TypedDict for graph state
│   └── workflow.py     # Graph topology and edges
└── utils/              # Helper utilities (logging, etc.)
```

### Running Tests

(Instructions for running tests would go here, e.g., `pytest`)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
