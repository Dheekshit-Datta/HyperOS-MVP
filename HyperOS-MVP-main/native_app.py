import webview
import threading
import os
import sys

# This script will act as the Native Desktop Host for HyperOS
# It creates a transparent, always-on-top window that loads the React logic

def start_native_app():
    # 1. Start the React/Vite server or use a built dist
    # For now, we point to the dev server if it's running, or index.html
    url = 'http://localhost:5173/'
    
    print("Launching HyperOS Native Desktop Overlay...")
    
    window = webview.create_window(
        'HyperOS Agent',
        url,
        transparent=True,
        on_top=True,
        frameless=True,
        width=1280,   # Full screen or large overlay
        height=800,
        background_color='#00000000' # Fully transparent
    )
    
    # Enable click-through logic: 
    # This usually requires native platform calls, 
    # but pywebview handles transparency well.
    
    webview.start(debug=True)

if __name__ == '__main__':
    start_native_app()
