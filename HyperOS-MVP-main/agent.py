"""
Core agent that runs analyze-plan-execute loop
Exactly like Claude Cowork agent but with Mistral
"""
import time
from screen_capture import capture_screenshot
from mistral_api import ask_mistral_what_to_do
from action_executor import execute_action
from element_detector import detect_elements

class HyperOSAgent:
    def __init__(self):
        self.task_in_progress = False
        self.current_task = None
        self.conversation_history = []
        
    def execute_task(self, user_task):
        """
        Main agent loop - EXACTLY like Claude Cowork
        """
        print(f"\n📋 Task: {user_task}")
        self.task_in_progress = True
        self.current_task = user_task
        
        max_steps = 50
        step_count = 0
        
        while self.task_in_progress and step_count < max_steps:
            step_count += 1
            print(f"\n🔄 Step {step_count}/50")
            
            # STEP 1: ANALYZE - Take screenshot
            print("📸 ANALYZE: Capturing screenshot...")
            screenshot = capture_screenshot()
            
            # Detect elements on screen using OCR
            elements = detect_elements(screenshot)
            print(f"   Found {len(elements)} UI elements")
            
            # STEP 2: PLAN - Ask Mistral what to do next
            print("🤖 PLAN: Asking Mistral API...")
            mistral_response = ask_mistral_what_to_do(
                task=user_task,
                screenshot=screenshot,
                elements=elements,
                conversation_history=self.conversation_history
            )
            
            # Mistral responds with action to take
            action = mistral_response['action']
            reasoning = mistral_response['reasoning']
            
            print(f"   Mistral says: {reasoning}")
            print(f"   Action: {action['type']}")
            
            # Check if task is complete
            if action['type'] == 'task_complete':
                print("✅ Task completed successfully!")
                self.task_in_progress = False
                return {
                    "status": "success",
                    "message": action.get('message', 'Task completed'),
                    "steps": step_count
                }
            
            # STEP 3: EXECUTE - Perform the action
            print(f"⚡ EXECUTE: {action['type']}...")
            execution_result = execute_action(action)
            
            if execution_result['success']:
                print(f"   ✓ Action executed successfully")
            else:
                print(f"   ✗ Action failed: {execution_result['error']}")
            
            # Add to conversation history
            self.conversation_history.append({
                "screenshot": screenshot,
                "action": action,
                "result": execution_result
            })
            
            # Wait for UI to update
            time.sleep(1.5)
        
        return {
            "status": "incomplete",
            "message": "Max steps reached",
            "steps": step_count
        }
