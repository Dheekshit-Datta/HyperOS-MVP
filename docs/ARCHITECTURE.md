# HyperOS Architecture

## Overview

HyperOS is a vision-enabled desktop AI agent that operates as a transparent overlay on Windows, macOS, and Linux. It uses Google's Gemini 1.5 Flash Vision AI to understand screen content and execute multi-step automation tasks.

---

## System Components

### 1. Electron Shell

**Purpose:** Desktop application wrapper providing transparent overlay and system integration.

**Key Features:**
- Transparent, frameless, always-on-top window
- Global hotkey registration (Ctrl+Space)
- Click-through support for non-interactive areas
- System tray icon with menu
- Secure IPC bridge between main and renderer processes

**Files:**
- `electron/main.ts` - Main Electron process
- `electron/preload.ts` - Secure IPC preload script

**Security:**
- `nodeIntegration: false`
- `contextIsolation: true`
- `sandbox: true`
- Channel whitelisting in preload

---

### 2. React Frontend

**Purpose:** User interface for task input and step visualization.

**Key Features:**
- Material glassmorphism design
- Real-time step visualization (Analyze → Plan → Execute)
- Animated transitions and loading states
- Error handling with toast notifications
- Dynamic click-through toggle

**Files:**
- `src/App.tsx` - Main React component
- `src/index.css` - TailwindCSS styles
- `src/main.tsx` - React entry point

**State Management:**
- Local React state with useState hooks
- No external state library needed

---

### 3. Python Backend (Agent Core)

**Purpose:** AI-powered automation engine with screen capture and action execution.

**Key Features:**
- FastAPI REST server on port 8000
- Gemini 1.5 Flash Vision AI integration
- Screen capture via pyautogui
- Action execution (click, type, press_key, wait)
- Window detection via pygetwindow
- Cancellation support with thread safety

**Files:**
- `agent-core/agent.py` - HyperOSAgent class
- `agent-core/main.py` - FastAPI server
- `agent-core/tools/window_manager.py` - Window utilities

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERACTION                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. User presses Ctrl+Space                                                  │
│     → Electron globalShortcut triggers                                       │
│     → Window visibility toggles                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. User types task: "Open Notepad and type Hello"                          │
│     → React captures input                                                   │
│     → POST request to http://127.0.0.1:8000/execute                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. FastAPI receives request                                                 │
│     → Validates task (1-1000 chars)                                         │
│     → Checks if agent is already running                                    │
│     → Calls agent.run_task(task)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. ANALYZE-PLAN-EXECUTE LOOP (max 20 iterations)                           │
│                                                                              │
│     ┌────────────────────────────────────────────────────────┐              │
│     │  STEP 1: CAPTURE                                       │              │
│     │  → pyautogui.screenshot()                              │              │
│     │  → Returns PIL.Image of current screen                 │              │
│     └────────────────────────────────────────────────────────┘              │
│                          │                                                   │
│                          ▼                                                   │
│     ┌────────────────────────────────────────────────────────┐              │
│     │  STEP 2: ANALYZE + PLAN (Gemini 1.5 Flash)            │              │
│     │  → Send screenshot + task + history to Gemini          │              │
│     │  → Gemini returns JSON:                                │              │
│     │    {                                                   │              │
│     │      "thinking": "I see the desktop with...",          │              │
│     │      "action": "click",                                │              │
│     │      "parameters": {"x": 500, "y": 300},               │              │
│     │      "done": false                                     │              │
│     │    }                                                   │              │
│     └────────────────────────────────────────────────────────┘              │
│                          │                                                   │
│                          ▼                                                   │
│     ┌────────────────────────────────────────────────────────┐              │
│     │  STEP 3: EXECUTE                                       │              │
│     │  → parse action type                                   │              │
│     │  → call pyautogui.click(500, 300)                      │              │
│     │  → wait 1 second for UI response                       │              │
│     └────────────────────────────────────────────────────────┘              │
│                          │                                                   │
│                          ▼                                                   │
│     ┌────────────────────────────────────────────────────────┐              │
│     │  Check: action == "done" or done == true?              │              │
│     │  → Yes: Return success                                 │              │
│     │  → No:  Loop back to STEP 1                            │              │
│     └────────────────────────────────────────────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Response returned to React                                               │
│     → UI updates with step history                                          │
│     → User sees Analyze → Plan → Execute visualization                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Desktop Shell** | Electron 28 | Cross-platform, transparent windows, global shortcuts |
| **Frontend** | React 18 + TypeScript | Type-safe, component-based, fast development |
| **Styling** | TailwindCSS 3.4 | Utility-first, rapid prototyping, consistent design |
| **Backend** | FastAPI + Uvicorn | Async, auto-docs, Python ecosystem access |
| **AI Engine** | Gemini 1.5 Flash | Best vision-language model, fast, generous free tier |
| **Automation** | pyautogui | Cross-platform mouse/keyboard control |
| **Window Detection** | pygetwindow | Window title and focus management |
| **Build** | Vite, electron-builder | Fast builds, easy packaging |

---

## Security Model

### Risks

1. **Arbitrary Action Execution**
   - The agent can click anywhere and type anything
   - Could expose passwords if visible on screen
   - Could execute unintended system commands

2. **Screen Content Sent to Cloud**
   - Screenshots are sent to Google's Gemini API
   - Sensitive information may be visible

3. **Local Network Exposure**
   - FastAPI server runs on localhost
   - CORS is configured for specific origins only

### Mitigations

| Risk | Mitigation |
|------|------------|
| API Key exposure | Stored in `.env`, gitignored |
| Arbitrary commands | 20-step limit, cancellation support |
| CORS attacks | Whitelist localhost:5173 only |
| IPC vulnerabilities | Channel whitelisting in preload |
| Runaway automation | pyautogui.FAILSAFE enabled (move mouse to corner) |

### Recommended Improvements

1. **Action Allowlist** - Define permitted actions/applications
2. **Screen Region Masking** - Blur sensitive areas before sending to AI
3. **Audit Logging** - Log all actions to disk
4. **Sandboxed Execution** - Run in VM or container

---

## Directory Structure

```
HyperOS-MVP/
│
├── agent-core/                  # Python Backend
│   ├── agent.py                 # Core agent logic (380 lines)
│   │   ├── class HyperOSAgent
│   │   ├── capture_screen()
│   │   ├── ai_model_analyze_plan_execute()
│   │   ├── execute_action()
│   │   └── run_task()
│   ├── main.py                  # FastAPI server (200 lines)
│   │   ├── GET /
│   │   ├── POST /execute
│   │   ├── POST /cancel
│   │   └── GET /status
│   ├── tools/
│   │   └── window_manager.py    # Window utilities
│   └── tests/
│       └── test_agent_core.py   # Unit tests
│
├── electron/                    # Electron Shell
│   ├── main.ts                  # Main process
│   │   ├── createWindow()
│   │   ├── createTray()
│   │   ├── registerShortcuts()
│   │   └── setupIPC()
│   └── preload.ts               # IPC bridge
│       ├── window.hyperOS
│       └── window.ipcRenderer
│
├── src/                         # React Frontend
│   ├── App.tsx                  # Main component (330 lines)
│   │   ├── State management
│   │   ├── API calls
│   │   ├── Click-through handling
│   │   └── Step visualization
│   ├── main.tsx                 # Entry point
│   ├── index.css                # TailwindCSS
│   └── vite-env.d.ts            # Type declarations
│
├── docs/                        # Documentation
│   ├── API.md
│   └── ARCHITECTURE.md
│
└── Config files
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    └── electron-builder.yml
```

---

## Performance Considerations

### Latency Breakdown (typical)

| Step | Duration |
|------|----------|
| Screen capture | ~50ms |
| Image encoding | ~100ms |
| Gemini API call | ~1-3s |
| Action execution | ~100ms |
| UI delay | ~1000ms |
| **Total per step** | **~2-4s** |

### Optimizations Applied

- Gemini 1.5 **Flash** (faster than Pro)
- JSON response mode (no parsing)
- Screenshot sent as PIL Image (no base64)
- 1-second delay is configurable

### Future Optimizations

- Streaming responses for real-time UI updates
- Screenshot caching if screen unchanged
- Parallel action planning
- Local model fallback (Ollama)

---

## Deployment Options

### 1. Development Mode (Current)
```bash
./start.bat   # or ./start.sh
```
- Backend runs in terminal
- Frontend runs via Vite dev server
- Hot reload enabled

### 2. Production Build
```bash
npm run electron:build
```
- Creates packaged `.exe` / `.dmg` / `.AppImage`
- Backend bundled as extra resource
- Requires separate Python installer or embedded Python

### 3. Cloud Deployment (Future)
- Deploy backend to cloud (AWS Lambda, Google Cloud Run)
- Agent runs locally, API calls to cloud
- Enables model switching without local updates
