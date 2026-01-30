"""
HyperOS Security Utilities
Input validation, audit logging, rate limiting, and safety checks
"""

import re
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
from functools import wraps
from dataclasses import dataclass
import json
import threading

logger = logging.getLogger('HyperOS.Security')


# =============================================================================
# BLOCKED KEYWORDS - Warn when these appear in task or on-screen analysis
# =============================================================================

BLOCKED_KEYWORDS = [
    # Credentials
    "password", "passwd", "secret", "credential", "api_key", "apikey",
    "access_token", "auth_token", "bearer", "private_key",
    
    # Financial
    "credit card", "creditcard", "card number", "cvv", "ccv",
    "bank account", "routing number", "social security", "ssn",
    
    # Personal
    "passport", "driver license", "date of birth", "dob",
    
    # System
    "sudo", "admin password", "root password", "registry",
]

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",           # Dangerous delete
    r"format\s+[a-z]:",    # Format drive
    r"del\s+/[sf]",        # Force delete
    r"shutdown",           # System shutdown
    r"taskkill\s+/f",      # Force kill process
]


# =============================================================================
# INPUT VALIDATION
# =============================================================================

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_input: str
    warnings: List[str]
    blocked: bool
    reason: Optional[str] = None


def validate_task_input(task: str) -> ValidationResult:
    """
    Validate and sanitize user task input.
    
    Args:
        task: Raw user input
        
    Returns:
        ValidationResult with sanitized input and any warnings
    """
    warnings = []
    blocked = False
    reason = None
    
    # Check for empty input
    if not task or not task.strip():
        return ValidationResult(
            is_valid=False,
            sanitized_input="",
            warnings=[],
            blocked=True,
            reason="Empty task input"
        )
    
    # Strip and limit length
    sanitized = task.strip()[:1000]
    
    # Check for blocked keywords
    task_lower = sanitized.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in task_lower:
            warnings.append(f"Task contains sensitive keyword: '{keyword}'")
            logger.warning(f"Sensitive keyword detected in task: {keyword}")
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            blocked = True
            reason = f"Task contains potentially dangerous command pattern"
            logger.error(f"Dangerous pattern blocked: {pattern}")
            break
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
    
    # Limit consecutive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return ValidationResult(
        is_valid=not blocked,
        sanitized_input=sanitized,
        warnings=warnings,
        blocked=blocked,
        reason=reason
    )


# =============================================================================
# SAFE COORDINATE VALIDATION
# =============================================================================

class CoordinateSafety:
    """
    Validate that click coordinates are in safe areas of the screen.
    Prevents clicking dangerous areas like close buttons, system tray, etc.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Define dangerous zones (relative coordinates)
        self.dangerous_zones: List[Dict[str, Any]] = [
            # Top-right close button area
            {
                "name": "window_close_button",
                "x_min": screen_width - 50,
                "x_max": screen_width,
                "y_min": 0,
                "y_max": 40,
                "severity": "high"
            },
            # System tray area
            {
                "name": "system_tray",
                "x_min": screen_width - 200,
                "x_max": screen_width,
                "y_min": screen_height - 50,
                "y_max": screen_height,
                "severity": "medium"
            },
            # Start button area
            {
                "name": "start_menu",
                "x_min": 0,
                "x_max": 60,
                "y_min": screen_height - 60,
                "y_max": screen_height,
                "severity": "low"
            },
        ]
    
    def is_safe_coordinate(self, x: int, y: int) -> Tuple[bool, Optional[str]]:
        """
        Check if coordinates are in a safe area.
        
        Returns:
            Tuple of (is_safe, warning_message)
        """
        # Check bounds
        if x < 0 or x > self.screen_width or y < 0 or y > self.screen_height:
            return False, f"Coordinates ({x}, {y}) are outside screen bounds"
        
        # Check dangerous zones
        for zone in self.dangerous_zones:
            if (zone["x_min"] <= x <= zone["x_max"] and 
                zone["y_min"] <= y <= zone["y_max"]):
                
                if zone["severity"] == "high":
                    return False, f"Clicking in dangerous zone: {zone['name']}"
                else:
                    logger.warning(f"Click near sensitive zone: {zone['name']} at ({x}, {y})")
        
        return True, None
    
    def get_safe_zones(self) -> List[Dict[str, int]]:
        """Return the safe clickable areas"""
        return [
            {
                "x_min": 60,
                "x_max": self.screen_width - 60,
                "y_min": 50,
                "y_max": self.screen_height - 60
            }
        ]


# =============================================================================
# AUDIT LOGGING
# =============================================================================

class AuditLogger:
    """
    Secure audit logging for all agent actions.
    Logs are written to a tamper-evident format.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.lock = threading.Lock()
        self._last_hash = ""
    
    def log_action(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        task_id: str,
        user_task: Optional[str] = None,
        result: Optional[str] = None
    ) -> None:
        """
        Log an action to the audit trail.
        
        Args:
            action_type: Type of action (click, type, etc.)
            parameters: Action parameters (sanitized)
            task_id: Unique task identifier
            user_task: Original user request (sanitized)
            result: Action result
        """
        # Sanitize parameters - redact sensitive values
        safe_params = self._sanitize_params(parameters)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "action": action_type,
            "parameters": safe_params,
            "user_task": user_task[:100] if user_task else None,  # Truncate
            "result": result,
            "prev_hash": self._last_hash,
        }
        
        # Create hash chain for tamper evidence
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()[:16]
        self._last_hash = entry["hash"]
        
        with self.lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        
        logger.debug(f"Audit logged: {action_type} [{entry['hash']}]")
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or redact sensitive information from parameters"""
        safe = {}
        sensitive_keys = ["password", "key", "token", "secret", "credential"]
        
        for key, value in params.items():
            if any(s in key.lower() for s in sensitive_keys):
                safe[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                safe[key] = value[:100] + "...[TRUNCATED]"
            else:
                safe[key] = value
        
        return safe
    
    def get_recent_entries(self, count: int = 50) -> List[Dict[str, Any]]:
        """Read recent audit entries"""
        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except FileNotFoundError:
            pass
        
        return entries[-count:]


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Token bucket rate limiter to prevent abuse.
    Default: 10 tasks per minute
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self.lock = threading.Lock()
    
    def is_allowed(self) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            Tuple of (is_allowed, seconds_until_allowed)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        with self.lock:
            # Remove old entries
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest = self.requests[0]
                wait_time = int(oldest + self.window_seconds - now) + 1
                return False, wait_time
            
            # Allow request
            self.requests.append(now)
            return True, None
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window"""
        now = time.time()
        window_start = now - self.window_seconds
        
        with self.lock:
            # Remove old entries
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            return max(0, self.max_requests - len(self.requests))


# =============================================================================
# SENSITIVE DATA DETECTOR
# =============================================================================

class SensitiveDataDetector:
    """
    Detect sensitive information in text to prevent leakage.
    Used to warn about sensitive data on screen or in AI responses.
    """
    
    PATTERNS = {
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        "ssn": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        "api_key": r'\b[A-Za-z0-9_-]{32,}\b',
    }
    
    @classmethod
    def detect(cls, text: str) -> List[Dict[str, str]]:
        """
        Detect sensitive data patterns in text.
        
        Returns:
            List of detected patterns with type and masked value
        """
        detections = []
        
        for data_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text)
            for match in matches:
                # Mask the value
                if len(match) > 8:
                    masked = match[:4] + "*" * (len(match) - 8) + match[-4:]
                else:
                    masked = "*" * len(match)
                
                detections.append({
                    "type": data_type,
                    "masked_value": masked,
                    "warning": f"Detected {data_type.replace('_', ' ')} in content"
                })
        
        return detections
    
    @classmethod
    def contains_sensitive(cls, text: str) -> bool:
        """Quick check if text contains any sensitive patterns"""
        for pattern in cls.PATTERNS.values():
            if re.search(pattern, text):
                return True
        return False


# =============================================================================
# DECORATOR UTILITIES
# =============================================================================

def require_rate_limit(limiter: RateLimiter):
    """Decorator to apply rate limiting to a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            allowed, wait_time = limiter.is_allowed()
            if not allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Try again in {wait_time} seconds."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class SecurityViolation(Exception):
    """Exception raised when a security check fails"""
    pass


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Create global rate limiter (10 tasks per minute)
global_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

# Create global audit logger
audit_logger = AuditLogger()
