"""
run_pipeline.py

CLI entry point. Loads config.yaml, runs the batch extraction over
every file in raw_data_path, and prints a summary.

Usage:
    python run_pipeline.py --config config.yaml
"""

import argparse
import logging
from pathlib import Path

from orchestrator.config import load_config
from orchestrator.runner import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run PPTX/PDF context extraction over a directory")
    default_config = Path(__file__).resolve().with_name("config.yaml")
    parser.add_argument("--config", default=str(default_config), help="Path to config.yaml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    config = load_config(args.config)
    summary = run_pipeline(config)

    print("\n--- Summary ---")
    print(f"Processed: {len(summary['processed'])}")
    print(f"Skipped (unrecognized): {len(summary['skipped'])}")
    print(f"Failed: {len(summary['failed'])}")
    for failure in summary["failed"]:
        print(f"  - {failure['path']}: {failure['error']}")


if __name__ == "__main__":
    main()
