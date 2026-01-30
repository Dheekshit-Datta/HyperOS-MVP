"""
HyperOS Error Recovery
Retry logic, circuit breaker pattern, checkpointing, and fallback actions
"""

import time
import logging
import json
from typing import TypeVar, Callable, Optional, Any, Dict
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import threading
import pickle

logger = logging.getLogger('HyperOS.Recovery')

T = TypeVar('T')


# =============================================================================
# RETRY WITH BACKOFF
# =============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff
        retryable_exceptions: Tuple of exceptions that trigger retry
        on_retry: Optional callback called on each retry
        
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def call_api():
            return requests.get("https://api.example.com")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        if on_retry:
                            on_retry(e, attempt)
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed. Last error: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker"""
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents cascading failures by failing fast when a service is down.
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        
        @breaker
        def call_gemini_api():
            # ... API call
            pass
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
        name: str = "default"
    ):
        """
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before trying half-open
            success_threshold: Successes needed to close from half-open
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.name = name
        
        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._lock = threading.Lock()
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    @property
    def is_closed(self) -> bool:
        return self._state == CircuitState.CLOSED
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator usage"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker"""
        with self._lock:
            self._maybe_recover()
            
            if self._state == CircuitState.OPEN:
                raise CircuitOpenError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Service appears to be down."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _maybe_recover(self) -> None:
        """Check if we should try to recover from open state"""
        if self._state == CircuitState.OPEN:
            if self._stats.last_failure_time:
                elapsed = (datetime.now() - self._stats.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    logger.info(f"Circuit '{self.name}' entering half-open state")
                    self._state = CircuitState.HALF_OPEN
                    self._stats.successes = 0
    
    def _on_success(self) -> None:
        """Handle successful call"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._stats.successes += 1
                if self._stats.successes >= self.success_threshold:
                    logger.info(f"Circuit '{self.name}' closed after recovery")
                    self._state = CircuitState.CLOSED
                    self._stats.failures = 0
            elif self._state == CircuitState.CLOSED:
                self._stats.failures = 0  # Reset on success
    
    def _on_failure(self, error: Exception) -> None:
        """Handle failed call"""
        with self._lock:
            self._stats.failures += 1
            self._stats.last_failure_time = datetime.now()
            
            if self._state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit '{self.name}' reopened after failure in half-open")
                self._state = CircuitState.OPEN
            elif self._state == CircuitState.CLOSED:
                if self._stats.failures >= self.failure_threshold:
                    logger.error(
                        f"Circuit '{self.name}' opened after {self._stats.failures} failures"
                    )
                    self._state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Manually reset the circuit breaker"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._stats = CircuitBreakerStats()
            logger.info(f"Circuit '{self.name}' manually reset")


class CircuitOpenError(Exception):
    """Exception raised when circuit is open"""
    pass


# =============================================================================
# CHECKPOINT SYSTEM
# =============================================================================

@dataclass
class Checkpoint:
    """Represents a saved state checkpoint"""
    task_id: str
    step_number: int
    task_description: str
    history: list
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class CheckpointManager:
    """
    Manages state checkpoints for recovery from failures.
    Saves state before risky operations and enables rollback.
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    def save_checkpoint(
        self,
        task_id: str,
        step_number: int,
        task_description: str,
        history: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a checkpoint before a risky action.
        
        Returns:
            Checkpoint ID for later restoration
        """
        checkpoint = Checkpoint(
            task_id=task_id,
            step_number=step_number,
            task_description=task_description,
            history=history.copy(),
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        checkpoint_id = f"{task_id}_{step_number}_{int(time.time())}"
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        with self._lock:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({
                    "task_id": checkpoint.task_id,
                    "step_number": checkpoint.step_number,
                    "task_description": checkpoint.task_description,
                    "history": checkpoint.history,
                    "timestamp": checkpoint.timestamp.isoformat(),
                    "metadata": checkpoint.metadata
                }, f, indent=2)
        
        logger.debug(f"Checkpoint saved: {checkpoint_id}")
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Restore state from a checkpoint.
        
        Returns:
            Checkpoint data or None if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None
        
        with self._lock:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        checkpoint = Checkpoint(
            task_id=data["task_id"],
            step_number=data["step_number"],
            task_description=data["task_description"],
            history=data["history"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )
        
        logger.info(f"Checkpoint restored: {checkpoint_id}")
        return checkpoint
    
    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """Get the most recent checkpoint for a task"""
        checkpoints = list(self.checkpoint_dir.glob(f"{task_id}_*.json"))
        
        if not checkpoints:
            return None
        
        # Sort by modification time, get latest
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        checkpoint_id = latest.stem
        
        return self.restore_checkpoint(checkpoint_id)
    
    def cleanup_old_checkpoints(self, max_age_hours: int = 24) -> int:
        """
        Remove checkpoints older than max_age_hours.
        
        Returns:
            Number of checkpoints removed
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0
        
        with self._lock:
            for checkpoint_file in self.checkpoint_dir.glob("*.json"):
                if datetime.fromtimestamp(checkpoint_file.stat().st_mtime) < cutoff:
                    checkpoint_file.unlink()
                    removed += 1
        
        if removed:
            logger.info(f"Cleaned up {removed} old checkpoints")
        
        return removed


# =============================================================================
# FALLBACK ACTIONS
# =============================================================================

class FallbackActions:
    """
    Provides fallback actions when AI fails or produces invalid responses.
    """
    
    @staticmethod
    def get_safe_action() -> Dict[str, Any]:
        """Return a safe no-op action"""
        return {
            "action": "wait",
            "parameters": {"seconds": 1},
            "reason": "Fallback: waiting for manual intervention"
        }
    
    @staticmethod
    def get_retry_action() -> Dict[str, Any]:
        """Return an action to retry screen analysis"""
        return {
            "action": "wait",
            "parameters": {"seconds": 2},
            "reason": "Fallback: retrying after brief wait"
        }
    
    @staticmethod
    def get_abort_action(reason: str = "Unknown error") -> Dict[str, Any]:
        """Return an action to abort the task"""
        return {
            "action": "done",
            "parameters": {"reason": f"Task aborted: {reason}"},
            "done": True
        }
    
    @classmethod
    def handle_ai_failure(
        cls,
        error: Exception,
        retry_count: int,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Decide on fallback action based on AI failure.
        
        Args:
            error: The exception that occurred
            retry_count: Current retry attempt
            max_retries: Maximum retries allowed
            
        Returns:
            Fallback action dictionary
        """
        error_str = str(error).lower()
        
        # Rate limit error - wait longer
        if "rate" in error_str or "quota" in error_str:
            logger.warning("AI rate limited, using extended wait")
            return {
                "action": "wait",
                "parameters": {"seconds": 10},
                "reason": "Fallback: rate limited, waiting"
            }
        
        # API unavailable - abort
        if "unavailable" in error_str or "503" in error_str:
            return cls.get_abort_action("AI service unavailable")
        
        # Auth error - abort
        if "auth" in error_str or "key" in error_str or "401" in error_str:
            return cls.get_abort_action("API authentication failed")
        
        # Retry if under limit
        if retry_count < max_retries:
            return cls.get_retry_action()
        
        # Max retries exceeded - abort
        return cls.get_abort_action(f"Max retries exceeded: {error}")


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Circuit breaker for Gemini API
gemini_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=2,
    name="gemini_api"
)

# Checkpoint manager
checkpoint_manager = CheckpointManager()
