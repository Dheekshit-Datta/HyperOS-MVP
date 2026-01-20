import pygetwindow as gw

class WindowManager:
    @staticmethod
    def get_active_window_title():
        try:
            win = gw.getActiveWindow()
            if win:
                return win.title
            return "Unknown"
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown"

    @staticmethod
    def find_window(title_query):
        """Find a window by partial title match"""
        try:
            wins = gw.getWindowsWithTitle(title_query)
            if wins:
                return wins[0]
            return None
        except Exception:
            return None

    @staticmethod
    def focus_window(window_obj):
        try:
            if window_obj:
                window_obj.activate()
                return True
        except Exception:
            return False
        return False
