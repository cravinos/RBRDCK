from typing import Dict, List, Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    @abstractmethod
    def setup_webhook(self, config: Dict) -> Dict:
        pass
    
    @abstractmethod
    def handle_webhook(self, payload: Dict) -> Dict:
        pass
    
    @abstractmethod
    def send_notification(self, message: str, context: Dict) -> bool:
        pass

class IntegrationHub:
    def __init__(self):
        self._integrations: Dict[str, BaseIntegration] = {}
        self._webhooks: Dict[str, Dict] = {}
        self._event_handlers: Dict[str, List] = {}
        
    def register_integration(self, name: str, integration: BaseIntegration):
        """Register a new integration."""
        self._integrations[name] = integration
        logger.info(f"Registered integration: {name}")
        
    def setup_webhook(self, integration_name: str, config: Dict) -> Dict:
        """Setup webhook for specific integration."""
        try:
            if integration_name not in self._integrations:
                raise ValueError(f"Integration {integration_name} not found")
                
            result = self._integrations[integration_name].setup_webhook(config)
            self._webhooks[integration_name] = result
            logger.info(f"Setup webhook for {integration_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error setting up webhook for {integration_name}: {e}")
            raise
            
    def handle_webhook_event(self, integration_name: str, payload: Dict) -> Dict:
        """Handle incoming webhook event."""
        try:
            if integration_name not in self._integrations:
                raise ValueError(f"Integration {integration_name} not found")
                
            result = self._integrations[integration_name].handle_webhook(payload)
            self._process_event_handlers(integration_name, payload)
            return result
            
        except Exception as e:
            logger.error(f"Error handling webhook for {integration_name}: {e}")
            raise
            
    def register_event_handler(self, integration_name: str, handler: callable):
        """Register event handler for integration."""
        if integration_name not in self._event_handlers:
            self._event_handlers[integration_name] = []
        self._event_handlers[integration_name].append(handler)
        
    def _process_event_handlers(self, integration_name: str, payload: Dict):
        """Process all registered event handlers for an integration."""
        handlers = self._event_handlers.get(integration_name, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error in event handler for {integration_name}: {e}")
                
    def send_notification(self, integration_name: str, message: str, context: Dict = None) -> bool:
        """Send notification through specified integration."""
        try:
            if integration_name not in self._integrations:
                raise ValueError(f"Integration {integration_name} not found")
                
            return self._integrations[integration_name].send_notification(message, context or {})
            
        except Exception as e:
            logger.error(f"Error sending notification through {integration_name}: {e}")
            return False
            
    def get_integration_status(self, integration_name: str) -> Dict:
        """Get status of specific integration."""
        if integration_name not in self._integrations:
            raise ValueError(f"Integration {integration_name} not found")
            
        webhook = self._webhooks.get(integration_name, {})
        handlers = len(self._event_handlers.get(integration_name, []))
        
        return {
            "name": integration_name,
            "webhook_configured": bool(webhook),
            "webhook_url": webhook.get("url"),
            "event_handlers": handlers,
            "active": bool(webhook and handlers > 0)
        }