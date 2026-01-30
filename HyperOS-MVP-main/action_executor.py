"""
Action executor - performs REAL mouse clicks and keyboard input
Uses PyAutoGUI for actual desktop automation
"""
import pyautogui
import time

# Safety settings
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True  # Move mouse to corner to stop

def execute_action(action):
    """
    Execute the action that Mistral decided
    ACTUALLY performs the automation - NOT FAKE
    """
    
    try:
        action_type = action['type']
        
        if action_type == 'click':
            # REAL mouse click at coordinates
            x = action['x']
            y = action['y']
            print(f"   Clicking at ({x}, {y})")
            pyautogui.click(x, y)
            return {"success": True}
        
        elif action_type == 'type':
            # REAL keyboard typing
            text = action['text']
            print(f"   Typing: {text}")
            pyautogui.write(text, interval=0.05)
            return {"success": True}
        
        elif action_type == 'press_key':
            # REAL keyboard key press
            key = action['key']
            print(f"   Pressing key: {key}")
            pyautogui.press(key)
            return {"success": True}
        
        elif action_type == 'hotkey':
            # REAL keyboard shortcut
            keys = action['keys']
            print(f"   Hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return {"success": True}
        
        elif action_type == 'wait':
            # Wait for UI to load
            seconds = action['seconds']
            print(f"   Waiting {seconds} seconds...")
            time.sleep(seconds)
            return {"success": True}
        
        elif action_type == 'task_complete':
            # Task finished
            return {"success": True, "complete": True}
        
        else:
            print(f"   ⚠️ Unknown action type: {action_type}")
            return {"success": False, "error": f"Unknown action: {action_type}"}
            
    except Exception as e:
        print(f"   ❌ Execution error: {e}")
        return {"success": False, "error": str(e)}
