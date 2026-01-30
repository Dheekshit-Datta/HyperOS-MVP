# HyperOS Security Documentation

## Overview

HyperOS is a vision-enabled desktop AI agent with access to screen capture and input automation. This document outlines security considerations, mitigations, and best practices.

---

## Threat Model

### 1. Arbitrary Code Execution
**Threat:** The AI could be manipulated to execute harmful commands.  
**Severity:** Critical  
**Mitigations:**
- Blocked keyword detection for dangerous commands
- 20-step limit prevents runaway automation
- Rate limiting (10 tasks/minute)
- Audit logging of all actions

### 2. Sensitive Data Exposure
**Threat:** Screenshots sent to Gemini API may contain passwords, PII.  
**Severity:** High  
**Mitigations:**
- Sensitive data detection warns on common patterns
- Users advised to close sensitive applications
- No screenshots saved locally by default

### 3. Click Injection Attacks
**Threat:** Malicious tasks could close security dialogs or click "Yes".  
**Severity:** High  
**Mitigations:**
- Coordinate safety zones (blocks close buttons, system tray)
- pyautogui.FAILSAFE enabled (move to corner to stop)
- User confirmation for destructive actions

### 4. API Key Theft
**Threat:** Gemini API key could be exposed.  
**Severity:** Medium  
**Mitigations:**
- Keys stored in `.env` (gitignored)
- No keys in logs (redacted)
- Environment validation on startup

### 5. Local Network Attacks
**Threat:** Malicious website could send requests to localhost:8000.  
**Severity:** Medium  
**Mitigations:**
- CORS whitelist (only localhost:5173)
- No external network binding
- Rate limiting on all endpoints

---

## Security Controls

### Input Validation
```python
# All task inputs are validated
from security import validate_task_input
result = validate_task_input(user_task)
if not result.is_valid:
    raise SecurityViolation(result.reason)
```

### Rate Limiting
- 10 tasks per minute per client
- Automatic blocking with retry-after header
- Prevents abuse and runaway automation

### Audit Logging
All actions are logged to `logs/audit_YYYYMMDD.jsonl`:
```json
{
    "timestamp": "2026-01-30T22:45:00",
    "task_id": "abc123",
    "action": "click",
    "parameters": {"x": 500, "y": 300},
    "hash": "a1b2c3d4"
}
```

### Coordinate Safety
Blocks clicks in dangerous zones:
- Window close buttons (top-right)
- System tray area
- Start menu button

---

## User Best Practices

1. **Close sensitive applications** before using HyperOS
2. **Never ask HyperOS to enter passwords** - type them yourself
3. **Review audit logs** periodically in `logs/` folder
4. **Use emergency stop** - move mouse to screen corner
5. **Rotate API keys** monthly
6. **Run with minimum permissions** - don't run as Administrator

---

## API Key Rotation

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Update `agent-core/.env` with new key
4. Delete old key from Google Console
5. Restart HyperOS

---

## Incident Response

If you suspect a security issue:

1. **Stop HyperOS immediately** (Ctrl+C or move mouse to corner)
2. **Check audit logs** in `logs/audit_*.jsonl`
3. **Revoke API key** if potentially compromised
4. **Review recent actions** against expected behavior

---

## Responsible Disclosure

Found a security vulnerability? Please:

1. **Do NOT** open a public GitHub issue
2. Email: security@hyperos.example.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
4. We aim to respond within 48 hours

---

## Security Checklist

| Control | Status |
|---------|--------|
| No secrets in code | ✅ |
| Input validation | ✅ |
| Rate limiting | ✅ |
| Audit logging | ✅ |
| CSP headers | ✅ |
| Coordinate safety | ✅ |
| Sensitive data detection | ✅ |
| Circuit breaker | ✅ |
