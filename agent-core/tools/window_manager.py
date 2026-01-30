"""
HyperOS Window Manager - Utilities for window detection and control
Uses pygetwindow for cross-platform window management
"""

import logging
from typing import Optional, List, Dict, Any

import pygetwindow as gw

logger = logging.getLogger('WindowManager')


class WindowManager:
    """
    Static utility class for window management operations.
    Provides methods to detect, find, and focus windows.
    """
    
    @staticmethod
    def get_active_window_title() -> str:
        """
        Get the title of the currently active/focused window.
        
        Returns:
            Window title string, or "Unknown" if detection fails
        """
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                return active_window.title
            return "Unknown"
        except Exception as e:
            logger.warning(f"Failed to get active window: {e}")
            return "Unknown"
    
    @staticmethod
    def find_window_by_title(title_query: str) -> Optional[gw.Window]:
        """
        Find a window by partial title match (case-insensitive).
        
        Args:
            title_query: Partial or full window title to search for
            
        Returns:
            First matching Window object, or None if not found
        """
        try:
            # Get all windows with matching title
            windows = gw.getWindowsWithTitle(title_query)
            
            if windows:
                logger.debug(f"Found {len(windows)} windows matching '{title_query}'")
                return windows[0]
            
            # Try case-insensitive search
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if title_query.lower() in window.title.lower():
                    return window
            
            logger.debug(f"No windows found matching '{title_query}'")
            return None
            
        except Exception as e:
            logger.error(f"Error finding window '{title_query}': {e}")
            return None
    
    @staticmethod
    def focus_window(window_title: str) -> bool:
        """
        Focus (bring to front and activate) a window by its title.
        
        Args:
            window_title: Partial or full window title
            
        Returns:
            True if window was focused successfully, False otherwise
        """
        try:
            window = WindowManager.find_window_by_title(window_title)
            
            if window:
                # Restore if minimized
                if window.isMinimized:
                    window.restore()
                
                # Activate (bring to front and focus)
                window.activate()
                logger.info(f"Focused window: {window.title}")
                return True
            
            logger.warning(f"Could not find window to focus: {window_title}")
            return False
            
        except Exception as e:
            logger.error(f"Error focusing window '{window_title}': {e}")
            return False
    
    @staticmethod
    def list_all_windows() -> List[Dict[str, Any]]:
        """
        Get a list of all visible windows with their properties.
        
        Returns:
            List of dictionaries containing window information
        """
        try:
            all_windows = gw.getAllWindows()
            window_list = []
            
            for window in all_windows:
                # Skip windows with empty titles (usually system windows)
                if not window.title or not window.title.strip():
                    continue
                
                try:
                    window_info = {
                        "title": window.title,
                        "left": window.left,
                        "top": window.top,
                        "width": window.width,
                        "height": window.height,
                        "is_active": window.isActive,
                        "is_minimized": window.isMinimized,
                        "is_maximized": window.isMaximized
                    }
                    window_list.append(window_info)
                except Exception:
                    # Some window properties may not be accessible
                    window_list.append({"title": window.title})
            
            logger.debug(f"Found {len(window_list)} windows")
            return window_list
            
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return []
    
    @staticmethod
    def get_window_bounds(window_title: str) -> Optional[Dict[str, int]]:
        """
        Get the bounding rectangle of a window.
        
        Args:
            window_title: Partial or full window title
            
        Returns:
            Dictionary with left, top, width, height, or None if not found
        """
        try:
            window = WindowManager.find_window_by_title(window_title)
            
            if window:
                return {
                    "left": window.left,
                    "top": window.top,
                    "width": window.width,
                    "height": window.height,
                    "right": window.left + window.width,
                    "bottom": window.top + window.height
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting window bounds: {e}")
            return None
    
    @staticmethod
    def minimize_window(window_title: str) -> bool:
        """
        Minimize a window.
        
        Args:
            window_title: Partial or full window title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            window = WindowManager.find_window_by_title(window_title)
            if window:
                window.minimize()
                return True
            return False
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return False
    
    @staticmethod
    def maximize_window(window_title: str) -> bool:
        """
        Maximize a window.
        
        Args:
            window_title: Partial or full window title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            window = WindowManager.find_window_by_title(window_title)
            if window:
                window.maximize()
                return True
            return False
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return False
