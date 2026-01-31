"""
Structured pipeline runner with visualization and logging.
"""
from datetime import datetime
import json
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from healing_pipeline.core.engine import PipelineEngine
from healing_pipeline.utils.logging import setup_logging
from healing_pipeline.config import settings


class PipelineRunner:
    """Manages the complete tax compliance automation pipeline."""

    def __init__(self, max_retries: int = 3):
        """Initialize the pipeline runner."""
        self.max_retries = max_retries
        self.engine = PipelineEngine(retries=max_retries)
        self.results = {}

    def display_header(self):
        """Display pipeline header."""
        print("\n" + "=" * 80)
        print("🚀 TAX COMPLIANCE AUTOMATION PIPELINE")
        print("=" * 80)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Max Retries: {self.max_retries}")
        print(f"🔗 API Base URL: {settings.TAX_API_BASE_URL}")
        print("=" * 80 + "\n")

    def display_pipeline_flow(self):
        """Display the pipeline flow diagram."""
        flow = """
┌─────────────────────────────────────────────────────────────────┐
│                   PIPELINE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                              │
│  │ START        │                                              │
│  └──────┬───────┘                                              │
│         │                                                      │
│         ▼                                                      │
│  ┌──────────────────┐      ┌──────────────┐                  │
│  │ 1. INGEST NODE   │──NO──│ 2. ANALYZE   │                  │
│  │ (Fetch Data)     │      │ (AI Watchdog)│                  │
│  └────────┬─────────┘      └──────┬───────┘                  │
│           │ YES                   │                           │
│           ▼                       ▼                           │
│  ┌──────────────────┐      ┌──────────────┐                  │
│  │ 3. ENRICH NODE   │      │ 4. HEAL NODE │                  │
│  │ (Tax Calc)       │      │ (Execute     │                  │
│  │ (Validate Tax)   │      │  Strategy)   │                  │
│  └────────┬─────────┘      └──────┬───────┘                  │
│           │                       │                           │
│        ✓/✗                        │                           │
│         │                         │                           │
│    ┌────┴─────────────────────────┘                           │
│    │                                                           │
│    ▼                                                           │
│  ┌──────────────┐                                             │
│  │ SUCCESS      │ (Logged, Compliance Met)                    │
│  └──────────────┘                                             │
│    or (on max retries)                                        │
│  ┌──────────────┐                                             │
│  │ FAILURE      │ (Escalation or Manual Review)               │
│  └──────────────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
        """
        print(flow)

    def run(self) -> bool:
        """Execute the pipeline and return success status."""
        self.display_header()
        self.display_pipeline_flow()

        print("\n📋 PIPELINE EXECUTION STARTING...\n")

        try:
            result = self.engine.run()
            self.results['success'] = result
            return result
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}\n")
            self.results['error'] = str(e)
            return False

    def display_summary(self):
        """Display execution summary."""
        print("\n" + "=" * 80)
        print("📊 PIPELINE EXECUTION SUMMARY")
        print("=" * 80)

        if self.results.get('error'):
            print(f"❌ Status: FAILED")
            print(f"📝 Error: {self.results['error']}")
        elif self.results.get('success'):
            print("✅ Status: SUCCESS")
            print("✓ Data ingestion completed")
            print("✓ Tax calculation validated")
            print("✓ Compliance logging successful")
        else:
            print("⚠️  Status: UNKNOWN")

        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    def display_configuration(self):
        """Display configuration details."""
        print("\n" + "=" * 80)
        print("⚙️  CONFIGURATION")
        print("=" * 80)
        print(f"API Base URL:      {settings.TAX_API_BASE_URL}")
        print(f"Failover URL:      {getattr(settings, 'TAX_API_FAILOVER_URL', 'Not configured')}")
        print(f"TaxJar API Key:    {settings.TAXJAR_API_KEY[:8]}..." if settings.TAXJAR_API_KEY else "Not set")
        print(f"LLM Model:         {settings.LLM_MODEL}")
        print(f"Max Retries:       {settings.MAX_RETRIES}")
        print("=" * 80 + "\n")


def main():
    """Main entry point for the pipeline runner."""
    log_file = "pipeline_execution.log"
    setup_logging(log_file)

    runner = PipelineRunner(max_retries=3)
    runner.display_configuration()

    success = runner.run()
    runner.display_summary()

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
