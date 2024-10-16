# browser_plugins.py
from abc import ABC, abstractmethod

class BrowserPlugin(ABC):
    """Base class for browser plugins."""

    @abstractmethod
    def generate_bookmarks(self, resources, config):
        """Generates bookmarks for the specific browser."""
        pass