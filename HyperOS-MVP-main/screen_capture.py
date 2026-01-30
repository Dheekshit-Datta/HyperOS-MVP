"""
Screen capture - takes screenshots of desktop
"""
from PIL import ImageGrab
import numpy as np

def capture_screenshot():
    """
    Capture full desktop screenshot
    Returns PIL Image object
    """
    screenshot = ImageGrab.grab()
    return screenshot

def capture_region(x, y, width, height):
    """
    Capture specific region of screen
    """
    bbox = (x, y, x + width, y + height)
    screenshot = ImageGrab.grab(bbox)
    return screenshot
