import click
from .core.engine import PipelineEngine
from .utils.logging import setup_logging
from .config import settings

@click.command()
@click.option('--url', default=None, help='Override Base URL')
@click.option('--retries', default=None, type=int, help='Override Max Retries')
@click.option('--log-file', default='recovery.log', help='Log file path')
def main(url, retries, log_file):
    """Run the Self-Healing Automation Pipeline."""
    setup_logging(log_file)
    
    # Use config defaults if not provided via CLI
    engine = PipelineEngine(url=url, retries=retries)
    success = engine.run()
    
    if not success:
        exit(1)

if __name__ == '__main__':
    main()
