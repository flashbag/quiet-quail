#!/usr/bin/env python3
"""
Cron Pipeline - Stages 1 & 2 Only

Runs only the first two stages of the pipeline:
  1. Fetch the main jobs listing page
  2. Parse HTML to JSON

This is optimized for hourly cron execution.
Stages 3 & 4 (downloading individual pages and generating API) are run separately.
"""

import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def run_stage(stage_num, script_name):
    """Run a single stage script."""
    logging.info(f"\n{'='*70}")
    logging.info(f"Running Stage {stage_num}: {script_name}")
    logging.info(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            ["python3", f"scripts/{script_name}"],
            timeout=600  # 10 minute timeout per stage
        )
        
        if result.returncode != 0:
            logging.error(f"Stage {stage_num} failed with exit code {result.returncode}")
            return False
        
        return True
    
    except subprocess.TimeoutExpired:
        logging.error(f"Stage {stage_num} timed out after 10 minutes")
        return False
    except Exception as e:
        logging.error(f"Stage {stage_num} error: {e}")
        return False


def main():
    """Run cron pipeline (stages 1-2 only)."""
    
    logging.info("\n" + "="*70)
    logging.info("QUIET-QUAIL CRON PIPELINE (Fetch & Parse Only)")
    logging.info("="*70)
    
    stages = [
        (1, "1_fetch_main_page.py"),
        (2, "2_parse_html_to_json.py"),
    ]
    
    failed_stages = []
    
    for stage_num, script_name in stages:
        if not run_stage(stage_num, script_name):
            failed_stages.append((stage_num, script_name))
            # Continue to next stage even if this one fails
    
    # Summary
    logging.info("\n" + "="*70)
    logging.info("CRON PIPELINE COMPLETE")
    logging.info("="*70)
    
    if failed_stages:
        logging.warning(f"\n⚠️ {len(failed_stages)} stage(s) failed:")
        for stage_num, script_name in failed_stages:
            logging.warning(f"  - Stage {stage_num}: {script_name}")
        return 1
    else:
        logging.info("\n✓ All stages completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
