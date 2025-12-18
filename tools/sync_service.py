"""
Data Sync Service - Syncs data folder from remote VPS using scp
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SyncConfig:
    """Configuration for data sync via scp"""
    remote_host: str = ""
    remote_user: str = ""
    remote_path: str = "/home/user/Quiet-Quail/data"
    local_path: str = "./data"
    remote_port: int = 22
    
    @classmethod
    def from_file(cls, config_file: str = ".sync_config.json"):
        """Load config from JSON file"""
        if os.path.exists(config_file):
            with open(config_file) as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self, config_file: str = ".sync_config.json"):
        """Save config to JSON file"""
        data = {
            'remote_host': self.remote_host,
            'remote_user': self.remote_user,
            'remote_path': self.remote_path,
            'local_path': self.local_path,
            'remote_port': self.remote_port
        }
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ Sync config saved to {config_file}")


class DataSyncService:
    """Handles data synchronization from remote server using scp"""
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.local_path = Path(config.local_path).absolute()
        self.sync_log = self.local_path / ".sync_log"
        
    def sync(self) -> bool:
        """Execute data sync using scp"""
        logger.info(f"🔄 Starting data sync via scp")
        
        try:
            # Create local directory if it doesn't exist
            self.local_path.mkdir(parents=True, exist_ok=True)
            
            success = self._sync_scp()
            
            if success:
                self._log_sync("SUCCESS")
                logger.info("✅ Data sync completed successfully")
                
                # Consolidate jobs after successful sync
                logger.info("📦 Consolidating jobs...")
                self._consolidate_jobs()
                
            else:
                self._log_sync("FAILED")
                logger.error("❌ Data sync failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            self._log_sync(f"ERROR: {str(e)}")
            return False
    
    def _sync_scp(self) -> bool:
        """Sync using scp (secure copy)"""
        remote_spec = f"{self.config.remote_user}@{self.config.remote_host}:{self.config.remote_path}/"
        local_spec = str(self.local_path) + "/"
        
        cmd = [
            "scp",
            "-r",
            "-P", str(self.config.remote_port),
            "-v",  # Verbose for progress
            remote_spec,
            local_spec
        ]
        
        logger.info(f"📋 Connecting to {self.config.remote_user}@{self.config.remote_host}:{self.config.remote_path}")
        logger.info(f"📤 Transferring files to {local_spec}")
        
        try:
            # Run without capturing output to show real-time progress
            result = subprocess.run(cmd, check=True)
            logger.info(f"✓ Sync completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Scp failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            logger.error("✗ scp not found. Install OpenSSH.")
            return False
    
    def _consolidate_jobs(self) -> None:
        """Consolidate jobs after sync completes"""
        try:
            # Run consolidate_jobs.py script
            consolidate_script = Path(__file__).parent / "consolidate_jobs.py"
            result = subprocess.run(
                ["python", str(consolidate_script), "--force"],
                cwd=str(self.local_path.parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✓ Consolidated JSON created/updated")
            else:
                logger.warning(f"⚠ Consolidation completed with warnings: {result.stderr}")
                
        except FileNotFoundError:
            logger.warning("⚠ consolidate_jobs.py not found, skipping consolidation")
        except subprocess.TimeoutExpired:
            logger.warning("⚠ Consolidation timed out")
        except Exception as e:
            logger.warning(f"⚠ Consolidation error: {e}")
    
    def _log_sync(self, status: str):
        """Log sync operation"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "files_synced": len(list(self.local_path.rglob("*"))) if self.local_path.exists() else 0
            }
            
            logs = []
            if self.sync_log.exists():
                with open(self.sync_log) as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            logs = logs[-100:]
            
            with open(self.sync_log, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not write sync log: {e}")
    
    def get_sync_status(self) -> Dict:
        """Get current sync status and history"""
        try:
            if not self.sync_log.exists():
                return {
                    "status": "never",
                    "last_sync": None,
                    "history": []
                }
            
            with open(self.sync_log) as f:
                logs = json.load(f)
            
            return {
                "status": logs[-1]['status'] if logs else None,
                "last_sync": logs[-1]['timestamp'] if logs else None,
                "file_count": logs[-1].get('files_synced', 0) if logs else 0,
                "history": logs[-10:]
            }
        except Exception as e:
            logger.warning(f"Could not read sync status: {e}")
            return {"status": "error", "error": str(e)}


def setup_sync_config():
    """Interactive setup for sync configuration"""
    print("\n🔧 Data Sync Configuration")
    print("=" * 50)
    
    config = SyncConfig()
    
    config.remote_host = input("Remote host (e.g., 192.168.1.100): ").strip()
    config.remote_user = input("Remote user (e.g., ubuntu): ").strip()
    config.remote_path = input("Remote data path (default: /home/user/Quiet-Quail/data): ").strip() or "/home/user/Quiet-Quail/data"
    config.remote_port = int(input("Remote SSH port (default: 22): ").strip() or "22")
    config.local_path = input("Local path (default: ./data): ").strip() or "./data"
    
    config.save()
    print("\n✅ Configuration saved!")
    
    return config


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync data folder from remote VPS")
    parser.add_argument("--setup", action="store_true", help="Setup sync")
    parser.add_argument("--sync", action="store_true", help="Execute sync")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if args.setup:
        config = setup_sync_config()
    else:
        config = SyncConfig.from_file()
    
    service = DataSyncService(config)
    
    if args.status:
        status = service.get_sync_status()
        print("\n📊 Sync Status:")
        print(json.dumps(status, indent=2))
    elif args.sync:
        if not config.remote_host:
            print("❌ Not configured. Run: python tools/sync_service.py --setup")
            exit(1)
        success = service.sync()
        exit(0 if success else 1)
    else:
        parser.print_help()
