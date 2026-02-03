"""
HyperOS Agent Core - Vision-enabled desktop AI agent
Uses Gemini 1.5 Flash for screen analysis and action planning
"""

import os
import time
import json
import logging
import platform
import threading
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

import pyautogui
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Import error recovery tools
from error_recovery import (
    retry_with_backoff,
    gemini_circuit_breaker,
    checkpoint_manager,
    FallbackActions,
    CircuitOpenError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HyperOSAgent')

# Load environment variables
load_dotenv()

# Safety settings for pyautogui
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True


class ActionType(Enum):
    """Available action types for the agent"""
    CLICK = "click"
    TYPE = "type"
    PRESS_KEY = "press_key"
    WAIT = "wait"
    DONE = "done"


@dataclass
class ActionResult:
    """Result of an action execution"""
    success: bool
    action_type: str
    message: str
    error: Optional[str] = None


@dataclass
class AgentResponse:
    """Structured response from Gemini AI"""
    thinking: str
    action: str
    parameters: Dict[str, Any]
    done: bool


class HyperOSAgent:
    """
    Main HyperOS Agent class that orchestrates screen capture,
    AI analysis, and action execution.
    """
    
    MAX_STEPS = 20
    STEP_DELAY = 1.0  # seconds between steps
    
    def __init__(self) -> None:
        """Initialize the HyperOS Agent with Gemini AI"""
        self.os_type: str = platform.system()
        self.screen_size: Tuple[int, int] = pyautogui.size()
        self.current_task: Optional[str] = None
        self.history: List[Dict[str, Any]] = []
        self.is_running: bool = False
        self._cancel_requested: bool = False
        self._lock = threading.Lock()
        
        # Validate and configure Gemini API
        self._init_gemini()
        
        logger.info(f"HyperOS Agent initialized on {self.os_type}")
        logger.info(f"Screen resolution: {self.screen_size[0]}x{self.screen_size[1]}")
    
    def _init_gemini(self) -> None:
        """Initialize Gemini AI with API key validation"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Debug logging
        if not gemini_key:
             logger.error(f"Environment keys: {[k for k in os.environ.keys() if 'GEMINI' in k]}")
             logger.error(f"Current working dir: {os.getcwd()}")
        
        if not gemini_key:
            error_msg = (
                "CRITICAL: GEMINI_API_KEY not found in environment variables. "
                "Please set it in the .env file or as an environment variable."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(gemini_key) < 20:
            error_msg = "GEMINI_API_KEY appears to be invalid (too short)"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        genai.configure(api_key=gemini_key)
        # Try different model names for compatibility (with version suffixes)
        model_names = [
            'gemini-1.5-flash-002',  # Production-ready version
            'gemini-1.5-flash',      # Default
            'gemini-1.5-pro',        # Alternative
            'gemini-pro'             # Fallback
        ]
        self.model = None
        
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test if model works by checking its name
                logger.info(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize {model_name}: {e}")
                continue
        
        if not self.model:
            raise ValueError(
                "Failed to initialize any Gemini model. "
                "Please check your API key and ensure it has access to Gemini models. "
                "Get your API key at: https://makersuite.google.com/app/apikey"
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status information"""
        return {
            "os": self.os_type,
            "screen_resolution": f"{self.screen_size[0]}x{self.screen_size[1]}",
            "time": time.strftime("%H:%M:%S"),
            "is_running": self.is_running,
            "current_task": self.current_task
        }
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(OSError, pyautogui.FailSafeException)
    )
    def capture_screen(self) -> Image.Image:
        """
        Capture the current screen state.
        
        Returns:
            PIL Image of the current screen
        """
        logger.debug("Capturing screen...")
        try:
            screenshot = pyautogui.screenshot()
            logger.debug(f"Screen captured: {screenshot.size}")
            return screenshot
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            raise
    
    def _get_active_window_title(self) -> str:
        """Safely get the active window title"""
        try:
            from tools.window_manager import WindowManager
            return WindowManager.get_active_window_title()
        except Exception as e:
            logger.warning(f"Could not get active window title: {e}")
            return "Unknown"
    
    @gemini_circuit_breaker
    def ai_model_analyze_plan_execute(
        self, 
        user_task: str, 
        screenshot: Image.Image
    ) -> Optional[AgentResponse]:
        """
        Send screenshot to Gemini AI for analysis and get next action.
        
        Args:
            user_task: The user's task description
            screenshot: Current screen capture
            
        Returns:
            AgentResponse with thinking, action, parameters, and done flag
        """
        active_window = self._get_active_window_title()
        
        system_instructions = f"""You are HyperOS AI, an autonomous desktop automation agent.

SYSTEM CONTEXT:
- Operating System: {self.os_type}
- Screen Resolution: {self.screen_size[0]}x{self.screen_size[1]}
- Active Window: {active_window}

YOUR MISSION:
Analyze the screenshot and determine the SINGLE next action to complete the user's task.

AVAILABLE ACTIONS:
1. click - Click at screen coordinates
   Parameters: {{"x": int, "y": int}}
   
2. type - Type text (optionally at coordinates)
   Parameters: {{"text": str, "x": int (optional), "y": int (optional)}}
   
3. press_key - Press a keyboard key
   Parameters: {{"key": str}} (e.g., "enter", "tab", "escape", "ctrl+c")
   
4. wait - Wait for UI to update
   Parameters: {{"seconds": float}}
   
5. done - Task is complete
   Parameters: {{"reason": str}}

RESPONSE FORMAT (JSON only):
{{
    "thinking": "Your analysis of the current screen state and reasoning",
    "action": "click|type|press_key|wait|done",
    "parameters": {{}},
    "done": false
}}

RULES:
- Return ONLY valid JSON, no markdown or extra text
- Be precise with coordinates - aim for center of UI elements
- If task appears complete, set action to "done" and done to true
- If stuck or cannot proceed, set action to "done" with explanation
"""

        prompt = f"""{system_instructions}

USER TASK: {user_task}

PREVIOUS ACTIONS IN THIS SESSION:
{json.dumps(self.history[-5:], indent=2) if self.history else "None yet"}

Analyze the attached screenshot and provide the next action as JSON."""

        logger.info("Sending request to Gemini AI...")
        
        try:
            # Try with system_instruction parameter (newer API)
            response = self.model.generate_content(
                [prompt, screenshot],
                generation_config={"response_mime_type": "application/json"},
                system_instruction=system_instructions
            )
        except TypeError:
            # Fallback: system instructions already in prompt
            response = self.model.generate_content(
                [prompt, screenshot],
                generation_config={"response_mime_type": "application/json"}
            )
        
        content = response.text.strip()
        logger.debug(f"Raw Gemini response: {content[:200]}...")
        
        # Clean up response if wrapped in markdown
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON response
        data = json.loads(content)
        
        return AgentResponse(
            thinking=data.get("thinking", ""),
            action=data.get("action", "done"),
            parameters=data.get("parameters", {}),
            done=data.get("done", False)
        )
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action using pyautogui.
        
        Args:
            action: The action type (click, type, press_key, wait, done)
            parameters: Action-specific parameters
            
        Returns:
            ActionResult indicating success/failure
        """
        logger.info(f"Executing action: {action} with params: {parameters}")
        
        try:
            if action == ActionType.CLICK.value:
                x = parameters.get("x", 0)
                y = parameters.get("y", 0)
                
                # Validate coordinates
                if not (0 <= x <= self.screen_size[0] and 0 <= y <= self.screen_size[1]):
                    return ActionResult(
                        success=False,
                        action_type=action,
                        message="Invalid coordinates",
                        error=f"Coordinates ({x}, {y}) outside screen bounds"
                    )
                
                pyautogui.click(x, y)
                return ActionResult(
                    success=True,
                    action_type=action,
                    message=f"Clicked at ({x}, {y})"
                )
                
            elif action == ActionType.TYPE.value:
                text = parameters.get("text", "")
                x = parameters.get("x")
                y = parameters.get("y")
                
                # Click first if coordinates provided
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                    time.sleep(0.3)
                
                pyautogui.write(text, interval=0.05)
                return ActionResult(
                    success=True,
                    action_type=action,
                    message=f"Typed: '{text[:50]}{'...' if len(text) > 50 else ''}'"
                )
                
            elif action == ActionType.PRESS_KEY.value:
                key = parameters.get("key", "")
                
                # Handle key combinations (e.g., "ctrl+c")
                if "+" in key:
                    keys = key.split("+")
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key)
                    
                return ActionResult(
                    success=True,
                    action_type=action,
                    message=f"Pressed key: {key}"
                )
                
            elif action == ActionType.WAIT.value:
                seconds = parameters.get("seconds", 1.0)
                time.sleep(min(seconds, 10.0))  # Cap at 10 seconds
                return ActionResult(
                    success=True,
                    action_type=action,
                    message=f"Waited {seconds} seconds"
                )
                
            elif action == ActionType.DONE.value:
                reason = parameters.get("reason", "Task completed")
                return ActionResult(
                    success=True,
                    action_type=action,
                    message=reason
                )
                
            else:
                return ActionResult(
                    success=False,
                    action_type=action,
                    message="Unknown action type",
                    error=f"Action '{action}' is not recognized"
                )
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                action_type=action,
                message="Action failed",
                error=str(e)
            )
    
    def request_cancel(self) -> bool:
        """Request cancellation of the current task"""
        with self._lock:
            if self.is_running:
                self._cancel_requested = True
                logger.info("Cancel requested for current task")
                return True
            return False
    
    def run_task(self, user_task: str) -> Dict[str, Any]:
        """
        Execute the main Analyze-Plan-Execute loop for a task.
        
        Args:
            user_task: Natural language description of the task
            
        Returns:
            Dict with status, history, and any error messages
        """
        with self._lock:
            if self.is_running:
                return {
                    "status": "error",
                    "message": "Another task is already running"
                }
            self.is_running = True
            self._cancel_requested = False
        
        logger.info(f"Starting task: {user_task}")
        self.current_task = user_task
        self.history = []
        
        try:
            for step in range(self.MAX_STEPS):
                # Check for cancellation
                if self._cancel_requested:
                    logger.info("Task cancelled by user")
                    return {
                        "status": "cancelled",
                        "message": "Task was cancelled",
                        "history": self.history,
                        "steps_completed": step
                    }
                
                logger.info(f"\n{'='*50}")
                logger.info(f"STEP {step + 1}/{self.MAX_STEPS}")
                logger.info(f"{'='*50}")
                
                # STEP 1: Capture screen
                try:
                    screenshot = self.capture_screen()
                except Exception as e:
                    logger.error(f"Screen capture failed: {e}")
                    return {
                        "status": "error",
                        "message": f"Screen capture failed: {e}",
                        "history": self.history
                    }
                
                # STEP 2: Get AI decision
                try:
                    ai_response = self.ai_model_analyze_plan_execute(user_task, screenshot)
                except CircuitOpenError:
                    logger.error("Gemini circuit breaker is OPEN. Using fallback.")
                    fallback = FallbackActions.get_abort_action("AI service unavailable (Circuit Open)")
                    # Convert dict to AgentResponse-like object or handle directly
                    # Since existing code expects AgentResponse, let's create one (or modifying logic)
                    # Use a lightweight AgentResponse for fallback
                    ai_response = AgentResponse(
                        thinking="Circuit breaker open - service down",
                        action=fallback["action"],
                        parameters=fallback["parameters"],
                        done=fallback.get("done", False)
                    )
                except Exception as e:
                    logger.error(f"AI execution error: {e}")
                    # Use intelligent fallback
                    fallback = FallbackActions.handle_ai_failure(e, retry_count=0) # We handle retries in decorator/logic
                    ai_response = AgentResponse(
                        thinking=f"Error occurred: {e}",
                        action=fallback["action"],
                        parameters=fallback["parameters"],
                        done=fallback.get("done", False)
                    )

                if ai_response is None:
                    logger.warning("AI returned None. Using fallback.")
                    fallback = FallbackActions.get_retry_action()
                    ai_response = AgentResponse(
                        thinking="AI returned no response",
                        action=fallback["action"],
                        parameters=fallback["parameters"],
                        done=False
                    )

                logger.info(f"AI Thinking: {ai_response.thinking[:100]}...")
                logger.info(f"AI Action: {ai_response.action}")
                
                # Checkpoint state BEFORE action execution
                try:
                    checkpoint_manager.save_checkpoint(
                        task_id=f"task_{int(time.time())}", # Simple task ID
                        step_number=step + 1,
                        task_description=user_task,
                        history=self.history,
                        metadata={"action": ai_response.action}
                    )
                except Exception as cp_e:
                    logger.warning(f"Failed to save checkpoint: {cp_e}")
                
                # Record step in history
                step_record = {
                    "step": step + 1,
                    "thinking": ai_response.thinking,
                    "action": ai_response.action,
                    "parameters": ai_response.parameters,
                    "done": ai_response.done
                }
                self.history.append(step_record)
                
                # Check if task is complete
                if ai_response.done or ai_response.action == ActionType.DONE.value:
                    logger.info("✓ Task completed successfully")
                    return {
                        "status": "success",
                        "message": ai_response.parameters.get("reason", "Task completed"),
                        "history": self.history,
                        "steps_completed": step + 1
                    }
                
                # STEP 3: Execute action
                result = self.execute_action(ai_response.action, ai_response.parameters)
                step_record["result"] = {
                    "success": result.success,
                    "message": result.message,
                    "error": result.error
                }
                
                if not result.success:
                    logger.warning(f"Action failed: {result.error}")
                    # Continue anyway - AI might recover on next step
                
                # Delay before next step
                time.sleep(self.STEP_DELAY)
            
            # Max steps reached
            logger.warning("Maximum steps reached without completion")
            return {
                "status": "timeout",
                "message": f"Task did not complete within {self.MAX_STEPS} steps",
                "history": self.history,
                "steps_completed": self.MAX_STEPS
            }
            
        except Exception as e:
            logger.exception(f"Unexpected error during task execution: {e}")
            return {
                "status": "error",
                "message": str(e),
                "history": self.history
            }
        finally:
            with self._lock:
                self.is_running = False
                self._cancel_requested = False
                self.current_task = None
    
    def execute_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Public API method to execute a task instruction.
        
        Args:
            instruction: Natural language task description
            
        Returns:
            Task execution result
        """
        return self.run_task(instruction)


# Global agent instance (lazy initialization)
_agent_instance: Optional[HyperOSAgent] = None


def get_agent() -> HyperOSAgent:
    """Get or create the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HyperOSAgent()
    return _agent_instance
