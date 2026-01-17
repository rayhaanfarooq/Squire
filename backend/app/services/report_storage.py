"""
Report Storage Service
Stores the latest Manager Agent report (file-based for cross-process access)
"""
import json
from typing import Optional, Dict, Any
from threading import Lock
from datetime import datetime
from pathlib import Path

# File-based storage for cross-process access
REPORT_FILE = Path(__file__).parent.parent.parent / ".stub_queue" / "latest_report.json"
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

# In-memory cache for same-process access
_latest_report: Optional[Dict[str, Any]] = None
_report_lock = Lock()
_report_timestamp: Optional[str] = None


def store_report(report: Dict[str, Any]) -> None:
    """Store the latest manager report (file-based for cross-process access)"""
    global _latest_report, _report_timestamp
    timestamp = datetime.now().isoformat()
    
    # Update in-memory cache (for same-process access)
    with _report_lock:
        _latest_report = report
        _report_timestamp = timestamp
    
    # Write to file (for cross-process access)
    try:
        report_data = {
            "report": report,
            "timestamp": timestamp,
            "status": "available"
        }
        with open(REPORT_FILE, 'w') as f:
            json.dump(report_data, f, indent=2)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error writing report to file: {e}")


def get_latest_report() -> Optional[Dict[str, Any]]:
    """Get the latest manager report (reads from file for cross-process access)"""
    global _latest_report, _report_timestamp
    
    # Try to read from file first (for cross-process access)
    try:
        if REPORT_FILE.exists():
            with open(REPORT_FILE, 'r') as f:
                report_data = json.load(f)
                # Update in-memory cache
                with _report_lock:
                    _latest_report = report_data.get("report")
                    _report_timestamp = report_data.get("timestamp")
                return report_data
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error reading report from file: {e}")
    
    # Fallback to in-memory cache (for same-process access)
    with _report_lock:
        if _latest_report is None:
            return None
        return {
            "report": _latest_report,
            "timestamp": _report_timestamp,
            "status": "available"
        }


def clear_report() -> None:
    """Clear the stored report"""
    global _latest_report, _report_timestamp
    with _report_lock:
        _latest_report = None
        _report_timestamp = None

