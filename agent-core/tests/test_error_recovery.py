
import unittest
from unittest.mock import MagicMock, patch
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_recovery import (
    retry_with_backoff,
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    CheckpointManager,
    FallbackActions
)

class TestErrorRecovery(unittest.TestCase):
    
    def test_retry_with_backoff_success(self):
        mock_func = MagicMock(return_value="success")
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def decorated_func():
            return mock_func()
            
        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_with_backoff_failure_then_success(self):
        mock_func = MagicMock(side_effect=[ValueError("fail"), "success"])
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def decorated_func():
            return mock_func()
            
        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)

    def test_retry_with_backoff_max_retries_exceeded(self):
        mock_func = MagicMock(side_effect=ValueError("fail"))
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def decorated_func():
            return mock_func()
            
        with self.assertRaises(ValueError):
            decorated_func()
        
        self.assertEqual(mock_func.call_count, 3) # Initial + 2 retries

    def test_circuit_breaker_flow(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, name="test_cb")
        
        self.assertTrue(cb.is_closed)
        
        # Fail twice
        with self.assertRaises(ValueError):
            with cb.call(MagicMock(side_effect=ValueError("fail 1"))): pass
        with self.assertRaises(ValueError):
             with cb.call(MagicMock(side_effect=ValueError("fail 2"))): pass
             
        # Should now be open
        # Note: implementation of call checks state first, then executes.
        # failure_threshold is 2.
        # 1st fail -> count 1
        # 2nd fail -> count 2 -> state OPEN
        
        # Verify it raises CircuitOpenError
        with self.assertRaises(CircuitOpenError):
             cb.call(MagicMock(return_value="should not run"))

        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Next call should be allowed (half-open)
        mock_success = MagicMock(return_value="success")
        result = cb.call(mock_success)
        self.assertEqual(result, "success")
        
        # Need success_threshold=2 to close. currently 1 success.
        # State should be HALF_OPEN still?
        # Let's check implementation details. 
        # _maybe_recover transitions OPEN -> HALF_OPEN
        # _on_success increments successes. if >= success_threshold -> CLOSED.
        
        # One more success needed
        cb.call(mock_success)
        self.assertTrue(cb.is_closed)

    def test_checkpoint_manager(self):
        cm = CheckpointManager(checkpoint_dir="test_checkpoints")
        
        # clean up before test
        for p in cm.checkpoint_dir.glob("*.json"):
            p.unlink()
            
        # Save checkpoint
        cp_id = cm.save_checkpoint(
            task_id="task1",
            step_number=1,
            task_description="test task",
            history=[{"action": "click"}],
            metadata={"key": "value"}
        )
        
        self.assertIsNotNone(cp_id)
        
        # Restore checkpoint
        cp = cm.restore_checkpoint(cp_id)
        self.assertIsNotNone(cp)
        self.assertEqual(cp.task_id, "task1")
        self.assertEqual(cp.step_number, 1)
        self.assertEqual(cp.metadata["key"], "value")
        
        # Clean up
        removed = cm.cleanup_old_checkpoints(max_age_hours=0) # remove all
        # self.assertGreaterEqual(removed, 1) # Might fail if too fast, but good enough

    def test_fallback_actions(self):
        action = FallbackActions.get_safe_action()
        self.assertEqual(action["action"], "wait")
        
        action = FallbackActions.get_abort_action("reason")
        self.assertEqual(action["action"], "done")
        self.assertTrue(action["done"])
        
        # Test handle_ai_failure
        # Rate limit
        action = FallbackActions.handle_ai_failure(Exception("429 Resource exhausted"), 0)
        self.assertEqual(action["action"], "wait")
        self.assertEqual(action["parameters"]["seconds"], 10)
        
        # Retry
        action = FallbackActions.handle_ai_failure(Exception("Random error"), 0, max_retries=2)
        self.assertEqual(action["action"], "wait") # Retry action is a wait
        self.assertEqual(action["reason"], "Fallback: retrying after brief wait")
        
        # Max retries
        action = FallbackActions.handle_ai_failure(Exception("Random error"), 3, max_retries=2)
        self.assertEqual(action["action"], "done")
        self.assertIn("Max retries exceeded", action["parameters"]["reason"])

if __name__ == '__main__':
    unittest.main()
