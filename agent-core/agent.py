import os
import time
import base64
import json
import platform
import pyautogui
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class HyperOSAgent:
    def __init__(self):
        self.os_type = platform.system()
        self.screen_size = pyautogui.size()
        
        # Initialize Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("WARNING: GEMINI_API_KEY not found in .env")
        genai.configure(api_key=gemini_key)
        
        # We can use gemini-1.5-pro or gemini-1.5-flash
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.current_task = None
        self.history = []

    def get_system_status(self):
        return {
            "os": self.os_type,
            "screen_resolution": f"{self.screen_size[0]}x{self.screen_size[1]}",
            "time": time.strftime("%H:%M:%S")
        }

    def capture_screen(self):
        """STEP 1: ANALYZE (Screen Capture)"""
        screenshot = pyautogui.screenshot()
        # Resize for Gemini if needed, but flash handles large images well
        return screenshot

    def ai_model_analyze_plan_execute(self, user_task, screenshot):
        """
        Send screenshot to Gemini
        Gemini analyzes, plans, and tells us what action to execute next
        """
        
        system_instructions = f"""
        You are HyperOS AI, a desktop automation agent. 
        Current System: {self.os_type}
        Screen Resolution: {self.screen_size}
        
        Follow this 3-step cycle for every task: ANALYZE screen → PLAN actions → EXECUTE task.
        
        Your job:
        1. ANALYZE: What do you see on screen? List all UI elements with coordinates.
        2. PLAN: What is the next action to complete this task? 
        3. EXECUTE: Provide exact action to perform (click/type/press_key/wait/done).
        
        Respond ONLY in JSON format:
        {{
          "analysis": "description of screen state",
          "detected_elements": [
            {{"element": "Start button", "coords": [x, y]}}
          ],
          "next_action": {{
            "type": "click" | "type" | "press_key" | "wait" | "done",
            "target": "element name",
            "coords": [x, y],
            "text": "text to type (if type)",
            "key": "key to press (if press_key)",
            "duration": seconds (if wait),
            "reasoning": "why this action"
          }}
        }}
        """

        prompt = f"""
        User Task: {user_task}
        Previous Actions: {json.dumps(self.history[-5:])}
        
        Analyze the attached screenshot and determine the NEXT action as per the instructions.
        Respond ONLY with the JSON object.
        """

        try:
            # Gemini 1.5 can take a list of [prompt, image]
            response = self.model.generate_content([prompt, screenshot], 
                                                generation_config={"response_mime_type": "application/json"},
                                                system_instruction=system_instructions)
            
            content = response.text.strip()
            # Remove markdown if any (though response_mime_type should handle it)
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return None

    def execute_action(self, action):
        """STEP 3: EXECUTE (Perform Actions)"""
        print(f"EXECUTE: {action['type']} on {action.get('target', 'N/A')}")
        
        try:
            if action['type'] == 'click':
                x, y = action['coords']
                pyautogui.click(x, y)
            elif action['type'] == 'type':
                if 'coords' in action and action['coords']:
                    pyautogui.click(action['coords'][0], action['coords'][1])
                    time.sleep(0.5)
                pyautogui.write(action['text'], interval=0.1)
            elif action['type'] == 'press_key':
                pyautogui.press(action['key'])
            elif action['type'] == 'wait':
                time.sleep(action.get('duration', 1))
            elif action['type'] == 'done':
                return True
            
            # Wait for UI response
            time.sleep(2)
            return False
        except Exception as e:
            print(f"Execution failed: {e}")
            return False

    def run_task(self, user_task):
        """COMPLETE ANALYZE-PLAN-EXECUTE LOOP"""
        print(f"Starting HyperOS Agent (Gemini) for task: {user_task}")
        self.history = []
        max_steps = 20
        
        for step in range(max_steps):
            print(f"\n--- CYCLE {step + 1} ---")
            
            # STEP 1: ANALYZE (Screen Capture)
            screenshot = self.capture_screen()
            
            # STEP 1 & 2: ANALYZE & PLAN (AI Model)
            gemini_decision = self.ai_model_analyze_plan_execute(user_task, screenshot)
            
            if not gemini_decision:
                # Retry once if it fails
                time.sleep(1)
                gemini_decision = self.ai_model_analyze_plan_execute(user_task, screenshot)
                if not gemini_decision:
                    return {"status": "error", "message": "Failed to get decision from Gemini"}
            
            print(f"ANALYZE: {gemini_decision['analysis']}")
            print(f"PLAN: {gemini_decision['next_action']['reasoning']}")
            
            # Record for history
            self.history.append({
                "step": step + 1,
                "analysis": gemini_decision['analysis'],
                "action": gemini_decision['next_action']
            })
            
            # Check for completion
            if gemini_decision['next_action']['type'] == 'done':
                print("✓ Task completed successfully")
                return {"status": "success", "history": self.history}
            
            # STEP 3: EXECUTE
            is_done = self.execute_action(gemini_decision['next_action'])
            if is_done:
                return {"status": "success", "history": self.history}
                
        return {"status": "timeout", "message": "Maximum steps reached"}

    def execute_instruction(self, instruction: str):
        return self.run_task(instruction)

agent = HyperOSAgent()
