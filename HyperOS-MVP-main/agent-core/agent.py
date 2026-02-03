import os
import time
import base64
import json
import platform
import pyautogui
from PIL import Image, ImageDraw
import io
import base64
import random
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

class HyperOSAgent:
    def __init__(self):
        self.os_type = platform.system()
        self.screen_size = pyautogui.size()
        
        # Initialize Mistral
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_key:
            print("WARNING: MISTRAL_API_KEY not found in .env")
        
        self.client = Mistral(api_key=mistral_key)
        self.model_name = 'pixtral-12b-2409' # Using Pixtral for vision capabilities
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
        return screenshot

    def encode_image(self, image):
        # Apply standard Visual Guides (Set-of-Mark style)
        # This draws a coordinate grid that helps the AI be 100% precise
        draw = ImageDraw.Draw(image)
        w, h = image.size
        
        # Draw a subtle numbered grid (0-1000 scale)
        # Vertical lines every 100 units
        for i in range(0, 1001, 100):
            x = int(i * w / 1000)
            draw.line([(x, 0), (x, h)], fill=(0, 255, 255, 50), width=1)
            draw.text((x + 5, 5), str(i), fill=(0, 255, 255, 150))
            
        # Horizontal lines every 100 units
        for j in range(0, 1001, 100):
            y = int(j * h / 1000)
            draw.line([(0, y), (w, y)], fill=(0, 255, 255, 50), width=1)
            draw.text((5, y + 5), str(j), fill=(0, 255, 255, 150))
            
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def ai_model_analyze_plan_execute(self, user_task, screenshot, is_verification=False, last_action=None):
        """
        Send TAGGED screenshot to Mistral (Pixtral)
        Mistral analyze, plans, and tells us what action to execute next
        """
        
        system_instructions = f"""
        You are HyperOS AI, a HUMAN-LIKE desktop agent following the 'Comet Architecture'.
        Current System: {self.os_type}
        Screen Resolution: {self.screen_size}
        
        VISUAL CONTEXT:
        The screenshot has a light-cyan coordinate grid overlay [0-1000 scale].
        - Use these grid numbers to calculate PERFECT coordinates for your actions.
        - X-axis (0-1000) is horizontal (left to right).
        - Y-axis (0-1000) is vertical (top to bottom).
        
        GOAL: Complete user tasks using GUI interactions ONLY. 
        - DO NOT suggest terminal commands.
        - Perform actions exactly like a human: click Start, click Icons, click Menus.
        
        Respond ONLY in JSON format:
        {{
          "screen_analysis": {{
            "description": "What do you see relative to the grid?",
            "elements": [
              {{"name": "App Icon", "coords_1000": [x, y], "type": "icon|button|text"}}
            ]
          }},
          "next_action": {{
            "type": "click" | "type" | "press_key" | "scroll" | "wait" | "done",
            "target": "element name",
            "coords_1000": [x, y],
            "text": "text content",
            "key": "key name",
            "reasoning": "Semantic explanation of this human-like step",
            "expected_outcome": "Visual state change"
          }}
        }}
        """

        if is_verification:
            prompt_text = f"TASK: {user_task}\nVERIFY outcomes of {json.dumps(last_action)}. Look at the grid and determine the NEXT interaction."
        else:
            prompt_text = f"USER REQUEST: {user_task}\nAnalyze the desktop state using the coordinate grid and perform the next logical interaction."

        try:
            base64_image = self.encode_image(screenshot)
            
            messages = [
                {"role": "system", "content": system_instructions},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                    ]
                }
            ]

            response = self.client.chat.complete(model=self.model_name, messages=messages, response_format={"type": "json_object"})
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling Mistral: {e}")
            return None

    def execute_action(self, action):
        """STEP 3: EXECUTE (Human-like Fluidity)"""
        action_type = action.get('type')
        target = action.get('target', 'N/A')
        print(f"⚡ EXECUTING: {action_type} on {target}")
        
        try:
            if 'coords_1000' in action:
                # Convert grid coords to actual pixels
                x = int(action['coords_1000'][0] * self.screen_size.width / 1000)
                y = int(action['coords_1000'][1] * self.screen_size.height / 1000)
                
                print(f"   Moving mouse to ({x}, {y}) for {action_type}")
                
                # Randomized human-like movement speed (0.3s to 0.7s)
                import random
                duration = 0.4 + (random.random() * 0.3)
                
                # Move mouse to target
                pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
                
                if action_type == 'click':
                    pyautogui.click()
                elif action_type == 'type':
                    pyautogui.click() # Human clicks first to focus
                    time.sleep(0.3)
                    pyautogui.write(action.get('text', ''), interval=0.08)
                elif action_type == 'scroll':
                    # scrolls positive for up, negative for down
                    clicks = 300 if action.get('text') == 'up' else -300
                    pyautogui.scroll(clicks)
            
            elif action_type == 'press_key':
                print(f"   Pressing key: {action.get('key')}")
                pyautogui.press(action.get('key'))
            elif action_type == 'wait':
                duration = action.get('duration', 1.5)
                print(f"   Waiting for {duration} seconds...")
                time.sleep(duration)
            
            time.sleep(1.0)
            return True # Fixed return value
        except Exception as e:
            print(f"❌ Action failed: {e}")
            return False

    def run_cycle(self, user_task: str, history: list = None):
        """Perform ONE cycle: Analyze → Plan → Execute → Verify"""
        print(f"\n--- CYCLE START (Task: {user_task}) ---")
        if history is not None:
            self.history = history
        
        # 1. ANALYZE & PLAN
        print("📸 Capturing screenshot and asking AI...")
        screenshot = self.capture_screen()
        decision = self.ai_model_analyze_plan_execute(user_task, screenshot)
        
        if not decision:
            print("❌ AI decision failed")
            return {"status": "error", "message": "Failed to get decision from AI"}
        
        analysis = decision.get('screen_analysis', {})
        next_action = decision.get('next_action', {})
        
        print(f"🧠 AI Reasoning: {next_action.get('reasoning', 'N/A')}")
        
        # Check for early completion
        if next_action['type'] == 'done':
            print("✅ Task marked as DONE by AI")
            return {
                "status": "complete",
                "analysis": analysis,
                "action": next_action,
                "verification": None
            }
        
        # 3. EXECUTE
        success = self.execute_action(next_action)
        
        # 4. VERIFY
        print("🔍 Verifying action outcome...")
        verify_screenshot = self.capture_screen()
        verification = self.ai_model_analyze_plan_execute(
            user_task, 
            verify_screenshot, 
            is_verification=True, 
            last_action=next_action
        )
        
        print("--- CYCLE END ---\n")
        return {
            "status": "success",
            "analysis": analysis,
            "action": next_action,
            "verification": verification
        }

    def execute_instruction(self, instruction: str):
        """Main entry point for instructions"""
        print(f"🚀 HyperOS Instruction: {instruction}")
        return self.run_task(instruction)

    def run_task(self, user_task):
        """COMPLETE ANALYZE-PLAN-EXECUTE LOOP"""
        self.history = []
        for i in range(20):
            res = self.run_cycle(user_task)
            if res['status'] in ['complete', 'error']:
                return res
        return {"status": "timeout", "message": "Maximum steps reached"}

agent = HyperOSAgent()
