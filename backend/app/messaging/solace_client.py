"""
Solace PubSub+ Client Wrapper
Provides publish/subscribe functionality for Solace Agent Mesh (SAM) patterns
Stub mode works without actual Solace broker for development
Uses file-based queue for cross-process communication
"""
import json
import logging
import threading
import time
import os
import uuid
from pathlib import Path
from typing import Optional, Callable, Dict, List
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Solace SDK, fall back to stub mode if not available
try:
    from solace.messaging.messaging_service import MessagingService
    from solace.messaging.resources.topic import Topic
    from solace.messaging.resources.topic_subscription import TopicSubscription
    from solace.messaging.receiver.message_receiver import MessageHandler, InboundMessage
    from solace.messaging.config.authentication_strategy import BasicAuthentication
    SOLACE_AVAILABLE = True
except ImportError:
    SOLACE_AVAILABLE = False
    logger.warning("Solace SDK not available. Running in stub mode.")

# File-based stub broker for cross-process communication
STUB_QUEUE_DIR = Path(__file__).parent.parent.parent / ".stub_queue"
STUB_QUEUE_DIR.mkdir(exist_ok=True)

# In-memory subscribers for same-process communication (fallback)
_stub_subscribers: Dict[str, List[Callable]] = {}
_stub_lock = threading.Lock()

# Subscriber polling threads (one per topic)
_stub_polling_threads: Dict[str, threading.Thread] = {}


class SolaceClient:
    """Solace PubSub+ client for SAM event coordination"""
    
    def __init__(self):
        self.messaging_service: Optional[MessagingService] = None
        self.connected = False
        self.use_stub = not SOLACE_AVAILABLE or not settings.SOLACE_HOST
        
    def connect(self) -> bool:
        """Connect to Solace PubSub+ broker"""
        if self.connected:
            return True
        
        if self.use_stub:
            logger.info("Using stub mode (in-memory message broker)")
            self.connected = True
            return True
            
        if not SOLACE_AVAILABLE:
            logger.warning("Solace SDK not available. Using stub mode.")
            self.use_stub = True
            self.connected = True
            return True
            
        try:
            broker_props = {
                "solace.messaging.transport.host": settings.SOLACE_HOST,
                "solace.messaging.service.vpn-name": getattr(settings, "SOLACE_VPN", "default"),
                "solace.messaging.transport.connection.retries": 3,
                "solace.messaging.transport.connection.retry-wait-in-ms": 1000,
            }
            
            if settings.SOLACE_USERNAME and settings.SOLACE_PASSWORD:
                auth_strategy = BasicAuthentication.of(settings.SOLACE_USERNAME, settings.SOLACE_PASSWORD)
            else:
                logger.warning("No Solace credentials provided. Using stub mode.")
                self.use_stub = True
                self.connected = True
                return True
                
            messaging_service = MessagingService.builder().from_properties(broker_props)\
                .with_authentication_strategy(auth_strategy)\
                .with_reconnection_retry_strategy()\
                .build()
            
            self.messaging_service = messaging_service
            self.messaging_service.connect()
            self.connected = True
            logger.info(f"Connected to Solace broker at {settings.SOLACE_HOST}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Solace: {e}")
            logger.info("Running in stub mode (in-memory message broker)")
            self.use_stub = True
            self.connected = True
            return True
    
    def disconnect(self):
        """Disconnect from Solace broker"""
        if self.messaging_service and self.connected and not self.use_stub:
            try:
                self.messaging_service.disconnect()
                logger.info("Disconnected from Solace broker")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
        self.connected = False
    
    def publish(self, topic: str, payload: dict) -> bool:
        """
        Publish a message to a Solace topic
        
        Args:
            topic: Topic name (e.g., 'squire/analysis/start')
            payload: Message payload as dictionary
            
        Returns:
            True if published successfully (or in stub mode), False otherwise
        """
        if not self.connected:
            if not self.connect():
                return False
        
        # Stub mode: use file-based broker for cross-process communication
        if self.use_stub:
            logger.info(f"[STUB] Publishing to topic '{topic}': {json.dumps(payload, indent=2)}")
            
            # Deliver to in-process subscribers (same process)
            with _stub_lock:
                subscribers = _stub_subscribers.get(topic, [])
                for handler in subscribers:
                    try:
                        # Call handler in a thread to avoid blocking
                        threading.Thread(target=handler, args=(payload,), daemon=True).start()
                    except Exception as e:
                        logger.error(f"Error calling stub subscriber: {e}")
            
            # Write message to file-based queue for cross-process subscribers
            try:
                topic_dir = STUB_QUEUE_DIR / topic.replace("/", "_")
                topic_dir.mkdir(parents=True, exist_ok=True)
                
                message_file = topic_dir / f"{uuid.uuid4()}.json"
                with open(message_file, 'w') as f:
                    json.dump({
                        "topic": topic,
                        "payload": payload,
                        "timestamp": datetime.now().isoformat()
                    }, f)
                
                logger.debug(f"[STUB] Wrote message to {message_file}")
            except Exception as e:
                logger.error(f"Error writing message to file queue: {e}")
            
            return True
        
        try:
            # Real Solace implementation
            solace_topic = Topic.of(topic)
            publisher = self.messaging_service.create_direct_message_publisher_builder().build()
            publisher.start()
            
            message = self.messaging_service.message_builder()\
                .with_application_message_id(f"msg-{topic}")\
                .with_property("application", "squire")\
                .build(json.dumps(payload))
            
            publisher.publish(message, solace_topic)
            publisher.terminate()
            
            logger.info(f"Published to topic '{topic}': {json.dumps(payload, indent=2)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to topic '{topic}': {e}")
            return False
    
    def subscribe(self, topic: str, message_handler: Callable[[dict], None]):
        """
        Subscribe to a Solace topic
        
        Args:
            topic: Topic name to subscribe to
            message_handler: Callback function that receives message payload as dict
        """
        if not self.connected:
            if not self.connect():
                logger.error("Cannot subscribe: not connected to Solace")
                return
        
        # Stub mode: register handler and start file polling
        if self.use_stub:
            # Register in-process handler
            with _stub_lock:
                if topic not in _stub_subscribers:
                    _stub_subscribers[topic] = []
                _stub_subscribers[topic].append(message_handler)
            
            # Start file-based polling thread for cross-process messages
            if topic not in _stub_polling_threads:
                def poll_messages():
                    topic_dir = STUB_QUEUE_DIR / topic.replace("/", "_")
                    topic_dir.mkdir(parents=True, exist_ok=True)
                    processed_files = set()
                    
                    while True:
                        try:
                            # Read all message files in topic directory
                            if topic_dir.exists():
                                for msg_file in topic_dir.glob("*.json"):
                                    if msg_file.name in processed_files:
                                        continue
                                    
                                    try:
                                        with open(msg_file, 'r') as f:
                                            msg_data = json.load(f)
                                        
                                        # Call handler with payload
                                        try:
                                            message_handler(msg_data.get("payload", {}))
                                            processed_files.add(msg_file.name)
                                            # Delete processed message after a delay (allow other processes to read)
                                            time.sleep(0.1)
                                            msg_file.unlink(missing_ok=True)
                                        except Exception as e:
                                            logger.error(f"Error calling message handler: {e}")
                                    except Exception as e:
                                        logger.error(f"Error reading message file {msg_file}: {e}")
                            
                            time.sleep(0.5)  # Poll every 0.5 seconds
                        except Exception as e:
                            logger.error(f"Error in polling thread: {e}")
                            time.sleep(1)
                
                polling_thread = threading.Thread(target=poll_messages, daemon=True)
                polling_thread.start()
                _stub_polling_threads[topic] = polling_thread
            
            logger.info(f"[STUB] Subscribed to topic '{topic}' (file-based broker + in-memory)")
            return
        
        try:
            # Real Solace implementation
            topic_subscription = TopicSubscription.of(topic)
            receiver = self.messaging_service.create_direct_message_receiver_builder()\
                .with_subscriptions(topic_subscription)\
                .build()
            
            class SolaceMessageHandler(MessageHandler):
                def on_message(self, message: InboundMessage):
                    try:
                        payload_str = message.get_payload_as_string()
                        payload = json.loads(payload_str) if payload_str else {}
                        message_handler(payload)
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
            
            receiver.set_message_handler(SolaceMessageHandler())
            receiver.start()
            
            logger.info(f"Subscribed to topic '{topic}'")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic '{topic}': {e}")


# Global client instance
_solace_client: Optional[SolaceClient] = None


def get_solace_client() -> SolaceClient:
    """Get or create global Solace client instance"""
    global _solace_client
    if _solace_client is None:
        _solace_client = SolaceClient()
        _solace_client.connect()
    return _solace_client
