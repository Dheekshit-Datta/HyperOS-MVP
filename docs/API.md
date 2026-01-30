# HyperOS API Documentation

## Base URL

```
http://127.0.0.1:8000
```

---

## Endpoints

### 1. Health Check

Check if the agent is running and get system information.

**Request:**
```http
GET /
```

**Response:**
```json
{
    "status": "HyperOS Agent Active",
    "version": "1.1.0",
    "capabilities": [
        "screen_capture",
        "vision_analysis",
        "click_automation",
        "type_automation",
        "keyboard_control",
        "window_detection"
    ],
    "system": {
        "os": "Windows",
        "screen_resolution": "1920x1080",
        "time": "14:30:45",
        "is_running": false,
        "current_task": null
    }
}
```

---

### 2. Execute Task

Execute a natural language task using the AI agent.

**Request:**
```http
POST /execute
Content-Type: application/json

{
    "task": "Open Notepad and type Hello World"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | Yes | Natural language description of the task (1-1000 chars) |

**Response (Success):**
```json
{
    "status": "success",
    "message": "Task completed",
    "history": [
        {
            "step": 1,
            "thinking": "I see the Windows desktop with taskbar at bottom...",
            "action": "click",
            "parameters": {"x": 24, "y": 1060},
            "done": false
        },
        {
            "step": 2,
            "thinking": "The Start menu is now open...",
            "action": "type",
            "parameters": {"text": "notepad"},
            "done": false
        },
        {
            "step": 3,
            "thinking": "Notepad is now open with a blank document...",
            "action": "type",
            "parameters": {"text": "Hello World"},
            "done": false
        },
        {
            "step": 4,
            "thinking": "Text has been typed successfully...",
            "action": "done",
            "parameters": {"reason": "Task completed successfully"},
            "done": true
        }
    ],
    "steps_completed": 4
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Failed to get response from Gemini AI",
    "history": []
}
```

**Response (Timeout):**
```json
{
    "status": "timeout",
    "message": "Task did not complete within 20 steps",
    "history": [...],
    "steps_completed": 20
}
```

**Response (Cancelled):**
```json
{
    "status": "cancelled",
    "message": "Task was cancelled",
    "history": [...],
    "steps_completed": 3
}
```

---

### 3. Cancel Task

Cancel the currently running task.

**Request:**
```http
POST /cancel
```

**Response (Task Running):**
```json
{
    "success": true,
    "message": "Cancel request sent. Task will stop after current step."
}
```

**Response (No Task):**
```json
{
    "success": false,
    "message": "No task is currently running"
}
```

---

### 4. Get Status

Get the current agent status without executing anything.

**Request:**
```http
GET /status
```

**Response:**
```json
{
    "is_running": true,
    "current_task": "Open Notepad",
    "system": {
        "os": "Windows",
        "screen_resolution": "1920x1080",
        "time": "14:32:10",
        "is_running": true,
        "current_task": "Open Notepad"
    }
}
```

---

## Action Types

The AI can return the following action types:

### click
Click at screen coordinates.
```json
{
    "action": "click",
    "parameters": {
        "x": 500,
        "y": 300
    }
}
```

### type
Type text, optionally at specific coordinates.
```json
{
    "action": "type",
    "parameters": {
        "text": "Hello World",
        "x": 500,  // optional
        "y": 300   // optional
    }
}
```

### press_key
Press a keyboard key or key combination.
```json
{
    "action": "press_key",
    "parameters": {
        "key": "enter"
    }
}
```

Supported key combinations:
- Single keys: `enter`, `tab`, `escape`, `backspace`, `delete`, `space`
- Arrow keys: `up`, `down`, `left`, `right`
- Combinations: `ctrl+c`, `ctrl+v`, `alt+tab`, `ctrl+shift+esc`

### wait
Wait for UI to update.
```json
{
    "action": "wait",
    "parameters": {
        "seconds": 2.0
    }
}
```
Note: Maximum wait time is capped at 10 seconds.

### done
Mark the task as complete.
```json
{
    "action": "done",
    "parameters": {
        "reason": "Task completed successfully"
    }
}
```

---

## Error Codes

| HTTP Code | Description |
|-----------|-------------|
| 200 | Success |
| 400 | Bad request (invalid task format) |
| 409 | Conflict (another task already running) |
| 500 | Internal server error |

---

## Rate Limits

- No explicit rate limits on the API
- Each task can take up to 20 steps
- Each step has a 1-second delay
- Maximum task duration: ~60-120 seconds

---

## Example: cURL

```bash
# Health check
curl http://127.0.0.1:8000/

# Execute task
curl -X POST http://127.0.0.1:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Open Calculator"}'

# Cancel task
curl -X POST http://127.0.0.1:8000/cancel

# Check status
curl http://127.0.0.1:8000/status
```

---

## Example: Python

```python
import requests

# Execute a task
response = requests.post(
    "http://127.0.0.1:8000/execute",
    json={"task": "Open Notepad"}
)
result = response.json()

for step in result.get("history", []):
    print(f"Step {step['step']}: {step['action']}")
```

---

## Example: JavaScript

```javascript
// Execute a task
const response = await fetch('http://127.0.0.1:8000/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task: 'Open Notepad' })
});

const result = await response.json();
console.log(result.status, result.message);
```
