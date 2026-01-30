"""
Unit tests for HyperOS Agent Core
Tests the main agent functionality with mocked dependencies
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHyperOSAgent(unittest.TestCase):
    """Test cases for the HyperOSAgent class"""
    
    @patch('agent.genai')
    @patch('agent.pyautogui')
    def setUp(self, mock_pyautogui, mock_genai):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {"GEMINI_API_KEY": "test_key_1234567890"})
        self.env_patcher.start()
        
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.PAUSE = 0.5
        mock_pyautogui.FAILSAFE = True
        
        from agent import HyperOSAgent
        self.agent = HyperOSAgent()
        self.mock_pyautogui = mock_pyautogui

    def tearDown(self):
        self.env_patcher.stop()

    def test_agent_initialization(self):
        """Test that agent initializes with correct properties"""
        self.assertEqual(self.agent.os_type, os.name == 'nt' and 'Windows' or self.agent.os_type)
        self.assertEqual(self.agent.screen_size, (1920, 1080))
        self.assertFalse(self.agent.is_running)
        self.assertIsNone(self.agent.current_task)
    
    def test_get_system_status(self):
        """Test system status returns correct structure"""
        status = self.agent.get_system_status()
        
        self.assertIn('os', status)
        self.assertIn('screen_resolution', status)
        self.assertIn('time', status)
        self.assertIn('is_running', status)
        self.assertEqual(status['screen_resolution'], '1920x1080')
    
    @patch('agent.pyautogui.screenshot')
    def test_capture_screen(self, mock_screenshot):
        """Test screen capture calls pyautogui"""
        mock_image = MagicMock()
        mock_image.size = (1920, 1080)
        mock_screenshot.return_value = mock_image
        
        result = self.agent.capture_screen()
        
        mock_screenshot.assert_called_once()
        self.assertEqual(result, mock_image)
    
    @patch('agent.pyautogui.click')
    def test_execute_action_click(self, mock_click):
        """Test click action execution"""
        result = self.agent.execute_action('click', {'x': 500, 'y': 300})
        
        mock_click.assert_called_with(500, 300)
        self.assertTrue(result.success)
        self.assertEqual(result.action_type, 'click')
    
    @patch('agent.pyautogui.click')
    def test_execute_action_click_invalid_coords(self, mock_click):
        """Test click action with invalid coordinates"""
        result = self.agent.execute_action('click', {'x': 5000, 'y': 300})
        
        mock_click.assert_not_called()
        self.assertFalse(result.success)
        self.assertIn('outside screen bounds', result.error)
    
    @patch('agent.pyautogui.write')
    def test_execute_action_type(self, mock_write):
        """Test typing action execution"""
        result = self.agent.execute_action('type', {'text': 'Hello World'})
        
        mock_write.assert_called_with('Hello World', interval=0.05)
        self.assertTrue(result.success)
        self.assertEqual(result.action_type, 'type')
    
    @patch('agent.pyautogui.click')
    @patch('agent.pyautogui.write')
    def test_execute_action_type_with_coords(self, mock_write, mock_click):
        """Test typing action with coordinates clicks first"""
        result = self.agent.execute_action('type', {
            'text': 'Test',
            'x': 100,
            'y': 100
        })
        
        mock_click.assert_called_with(100, 100)
        mock_write.assert_called()
        self.assertTrue(result.success)
    
    @patch('agent.pyautogui.press')
    def test_execute_action_press_key(self, mock_press):
        """Test key press action"""
        result = self.agent.execute_action('press_key', {'key': 'enter'})
        
        mock_press.assert_called_with('enter')
        self.assertTrue(result.success)
    
    @patch('agent.pyautogui.hotkey')
    def test_execute_action_press_key_combo(self, mock_hotkey):
        """Test key combination action"""
        result = self.agent.execute_action('press_key', {'key': 'ctrl+c'})
        
        mock_hotkey.assert_called_with('ctrl', 'c')
        self.assertTrue(result.success)
    
    @patch('agent.time.sleep')
    def test_execute_action_wait(self, mock_sleep):
        """Test wait action"""
        result = self.agent.execute_action('wait', {'seconds': 2})
        
        mock_sleep.assert_called_with(2)
        self.assertTrue(result.success)
    
    @patch('agent.time.sleep')
    def test_execute_action_wait_capped(self, mock_sleep):
        """Test wait action is capped at 10 seconds"""
        result = self.agent.execute_action('wait', {'seconds': 100})
        
        mock_sleep.assert_called_with(10.0)
        self.assertTrue(result.success)
    
    def test_execute_action_done(self):
        """Test done action"""
        result = self.agent.execute_action('done', {'reason': 'Task complete'})
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'Task complete')
    
    def test_execute_action_unknown(self):
        """Test unknown action returns failure"""
        result = self.agent.execute_action('unknown_action', {})
        
        self.assertFalse(result.success)
        self.assertIn('not recognized', result.error)
    
    def test_request_cancel_when_not_running(self):
        """Test cancel request when no task is running"""
        result = self.agent.request_cancel()
        self.assertFalse(result)
    
    def test_request_cancel_when_running(self):
        """Test cancel request when task is running"""
        self.agent.is_running = True
        result = self.agent.request_cancel()
        self.assertTrue(result)
        self.assertTrue(self.agent._cancel_requested)
    
    @patch('agent.HyperOSAgent.capture_screen')
    @patch('agent.HyperOSAgent.ai_model_analyze_plan_execute')
    def test_run_task_completes_on_done(self, mock_analyze, mock_capture):
        """Test run_task completes when AI returns done"""
        from agent import AgentResponse
        
        mock_capture.return_value = MagicMock()
        mock_analyze.return_value = AgentResponse(
            thinking="Task analysis",
            action="done",
            parameters={"reason": "Completed"},
            done=True
        )
        
        result = self.agent.run_task("Test task")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['history']), 1)
    
    @patch('agent.HyperOSAgent.capture_screen')
    @patch('agent.HyperOSAgent.ai_model_analyze_plan_execute')
    @patch('agent.HyperOSAgent.execute_action')
    @patch('agent.time.sleep')
    def test_run_task_executes_multiple_steps(self, mock_sleep, mock_execute, mock_analyze, mock_capture):
        """Test run_task executes multiple steps"""
        from agent import AgentResponse, ActionResult
        
        mock_capture.return_value = MagicMock()
        mock_execute.return_value = ActionResult(True, 'click', 'Clicked')
        
        # First call returns click, second returns done
        mock_analyze.side_effect = [
            AgentResponse(
                thinking="Need to click",
                action="click",
                parameters={"x": 100, "y": 100},
                done=False
            ),
            AgentResponse(
                thinking="Done now",
                action="done",
                parameters={"reason": "Finished"},
                done=True
            )
        ]
        
        result = self.agent.run_task("Multi-step task")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['history']), 2)
        self.assertEqual(mock_analyze.call_count, 2)
    
    @patch('agent.HyperOSAgent.capture_screen')
    @patch('agent.HyperOSAgent.ai_model_analyze_plan_execute')
    def test_run_task_handles_ai_failure(self, mock_analyze, mock_capture):
        """Test run_task handles AI failure by retrying until timeout"""
        mock_capture.return_value = MagicMock()
        # Simulate persistent failure
        mock_analyze.side_effect = Exception("AI Error")
        
        result = self.agent.run_task("Failing task")
        
        # Should timeout after retrying max steps
        self.assertEqual(result['status'], 'timeout')
        self.assertIn('did not complete', result['message'])
    
    def test_run_task_prevents_concurrent_execution(self):
        """Test that concurrent task execution is prevented"""
        self.agent.is_running = True
        
        result = self.agent.run_task("Concurrent task")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('already running', result['message'])


class TestAgentApiKeyValidation(unittest.TestCase):
    """Test API key validation"""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('agent.pyautogui')
    def test_missing_api_key_raises_error(self, mock_pyautogui):
        """Test that missing API key raises ValueError"""
        mock_pyautogui.size.return_value = (1920, 1080)
        
        # Remove GEMINI_API_KEY if it exists
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        from agent import HyperOSAgent
        
        with self.assertRaises(ValueError) as context:
            HyperOSAgent()
        
        self.assertIn('GEMINI_API_KEY', str(context.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
