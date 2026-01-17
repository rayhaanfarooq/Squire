"""
Join Agent - Synchronization Agent
Waits for both PR and Meeting analyses to complete
Subscribes to squire/analysis/pr/done and squire/analysis/meeting/done
Publishes to squire/analysis/join when both events are received
"""
import logging
import time
from threading import Lock
from app.messaging.solace_client import get_solace_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory state to track completion
_state_lock = Lock()
_pr_done = False
_meeting_done = False
_pr_result = None
_meeting_result = None


def reset_state():
    """Reset state for next workflow run"""
    global _pr_done, _meeting_done, _pr_result, _meeting_result
    with _state_lock:
        _pr_done = False
        _meeting_done = False
        _pr_result = None
        _meeting_result = None


def check_and_publish_join():
    """Check if both agents are done and publish join event if so"""
    global _pr_done, _meeting_done, _pr_result, _meeting_result
    
    with _state_lock:
        if _pr_done and _meeting_done:
            logger.info("Both PR and Meeting analyses complete. Publishing join event...")
            client = get_solace_client()
            
            join_payload = {
                "event": "join",
                "pr_analysis": _pr_result,
                "meeting_analysis": _meeting_result,
                "status": "ready_for_manager"
            }
            
            client.publish("squire/analysis/join", join_payload)
            logger.info("Join Agent published to squire/analysis/join with both results")
            
            print(f"\n{'='*60}")
            print("JOIN AGENT - SYNCHRONIZATION COMPLETE")
            print(f"{'='*60}")
            print(f"PR Analysis: {_pr_result.get('count', 0) if _pr_result else 0} PR(s) analyzed")
            print(f"Meeting Analysis: {_meeting_result.get('documents_analyzed', 0) if _meeting_result else 0} document(s) analyzed")
            print(f"{'='*60}\n")
            
            # Reset state for next run
            reset_state()


def handle_pr_done(payload: dict):
    """Handle PR Agent completion event"""
    global _pr_done, _pr_result
    logger.info("Join Agent received PR analysis results")
    
    with _state_lock:
        _pr_done = True
        _pr_result = payload
    
    check_and_publish_join()


def handle_meeting_done(payload: dict):
    """Handle Meeting Agent completion event"""
    global _meeting_done, _meeting_result
    logger.info("Join Agent received Meeting analysis results")
    
    with _state_lock:
        _meeting_done = True
        _meeting_result = payload
    
    check_and_publish_join()


def main():
    """Main function to run Join Agent"""
    logger.info("Starting Join Agent...")
    
    client = get_solace_client()
    client.subscribe("squire/analysis/pr/done", handle_pr_done)
    client.subscribe("squire/analysis/meeting/done", handle_meeting_done)
    logger.info("Join Agent subscribed to squire/analysis/pr/done and squire/analysis/meeting/done")
    
    try:
        logger.info("Join Agent is running. Waiting for both analyses to complete...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Join Agent shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()
