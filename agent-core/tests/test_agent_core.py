import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import HyperOSAgent

class TestHyperOSAgent(unittest.TestCase):

    @patch('agent.genai.GenerativeModel')
    @patch('agent.pyautogui')
    @patch('agent.os.getenv')
    def setUp(self, mock_getenv, mock_pyautogui, mock_model):
        mock_getenv.return_value = "fake_key"
        self.agent = HyperOSAgent()
        
        # Mock screen size
        self.agent.screen_size = (1920, 1080)

    @patch('agent.pyautogui.screenshot')
    def test_capture_screen(self, mock_screenshot):
        self.agent.capture_screen()
        mock_screenshot.assert_called_once()

    @patch('agent.HyperOSAgent.ai_model_analyze_plan_execute')
    @patch('agent.HyperOSAgent.execute_action')
    def test_run_task_flow(self, mock_execute, mock_analyze):
        """Test the main loop structure"""
        # Mock analysis to return a 'done' action immediately
        mock_analyze.side_effect = [
            {
                "analysis": "Test analysis",
                "detected_elements": [],
                "next_action": {
                    "type": "click",
                    "coords": [100, 100],
                    "reasoning": "Clicking test button"
                }
            },
            {
                "analysis": "Finished",
                "detected_elements": [],
                "next_action": {
                    "type": "done",
                    "reasoning": "Task complete"
                }
            }
        ]
        
        # Mock execute to return False then True (though done handles return)
        mock_execute.return_value = False 

        result = self.agent.run_task("Test task")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['history']), 2)
        self.assertEqual(mock_analyze.call_count, 2)

    @patch('agent.pyautogui.click')
    def test_execute_action_click(self, mock_click):
        action = {"type": "click", "coords": [500, 500]}
        self.agent.execute_action(action)
        mock_click.assert_called_with(500, 500)

    @patch('agent.pyautogui.write')
    def test_execute_action_type(self, mock_write):
        action = {"type": "type", "text": "hello"}
        self.agent.execute_action(action)
        mock_write.assert_called_with("hello", interval=0.1)

if __name__ == '__main__':
    unittest.main()
