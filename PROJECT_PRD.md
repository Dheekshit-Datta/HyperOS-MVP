# Product Requirements Document (PRD): HyperOS MVP

## 1. Product Vision
HyperOS strives to be the **ultimate "Iron Man" Desktop Assistant**—an omniscient, vision-enabled AI agent that lives transparently on your desktop. Unlike chatbots trapped in a browser tab, HyperOS sees what you see and interacts with your applications directly. It aims to bridge the gap between "chatting" with AI and "working" with AI, allowing users to delegate complex, multi-step workflows across different native applications just by asking.

## 2. User Personas
*   **The Power User / Developer**: Wants to automate repetitive workflows (e.g., "Take this JSON from VS Code, format it, and Slack it to the team"). Values speed, keyboard shortcuts, and deep system integration.
*   **The Multi-Tasker**: Juggles dozens of windows and needs an "executive assistant" to find information, summarize context, or perform quick lookups without context switching.

## 3. Current Feature Set (V1.0)
*   **Transparent Overlay UI**: An Electron-based, "always-on-top" window that allows click-through to underlying applications, maintaining user flow.
*   **Visual Intelligence**: Uses **Gemini 1.5 Flash** to "see" the user's screen.
*   **Natural Language Execution**: Translates user intent (e.g., "Open YouTube") into simulated mouse/keyboard actions via `pyautogui`.
*   **Analyze-Plan-Execute Loop**: A visible 3-step reasoning process (Analyze Screen -> Plan Action -> Execute) shown in the UI for transparency.
*   **Global Access**: Toggled via `Cmd/Ctrl + Space` for instant availability.

## 4. Functional Requirements
*   **Frontend-Backend Communication**: The React frontend must successfully send text commands to the Python backend via local HTTP (Port 8000).
*   **Screen Capture**: The backend must legally capture the screen content without blocking the UI.
*   **AI Latency**: The critical path (Capture -> API Call -> Action) must happen within < 3 seconds to feel responsive.
*   **Window Management**: The application must correctly handle focus stealing and returning focus to the target application.
*   **Safety**: The agent must have a "Start/Stop" mechanism (currently implied by the loop limit) to prevent runaway automation.

## 5. Technical Debt & Risks
*   **Fragile Vision-Only Control**: Reliance on `pyautogui` and coordinate prediction is brittle. If a button moves 5px or the model hallucinates coords, the action fails.
*   **Security Model**: Arbitrary shell command execution (`subprocess` in prototype) and lack of sandboxing pose significant security risks.
*   **Hardcoded Configuration**: API keys and backend URLs `http://127.0.0.1:8000` are hardcoded or rely on simple `.env` without validation. [PARTIALLY FIXED: Agent now validates API Key on boot]
*   **Dual Baselines**: Splitting logic between `hyperos_native.py` (legacy) and `agent-core` creates confusion. [IN PROGRESS: Window logic ported to `agent-core/tools/window_manager.py`]

## 6. V2.0 Roadmap: The "Best" Version
To elevate HyperOS from a "cool demo" to a robust daily driver, the following features are prioritized for V2.0:

### 6.1. Local RAG (Privacy & Context)
*   **Why**: Users work with private files (PDFs, docs, codebases) that shouldn't always be uploaded to the cloud.
*   **What**: Integrate a local vector database (e.g., ChromaDB) to index user-specified folders.
*   **Impact**: Enables "Chat with your codebase" or "Summarize this local PDF" entirely offline or with hybrid processing.

### 6.2. System-Level Automation (Accessibility APIs)
*   **Why**: Vision is slow and inaccurate for precise clicking.
*   **What**: Integrate **Windows UI Automation** (via `pywinauto` or `uiautomation`).
*   **How**: The Agent should query the Accessibility Tree to find the "Send" button handle directly, rather than guessing (x,y) pixels. Vision becomes a fallback or verifier.
*   **Impact**: 100% reliable clicking and text injection, even if windows move.

### 6.3. Cross-App Context Awareness
*   **Why**: Work doesn't happen in silos.
*   **What**: Maintain a "Context Graph" of recent activities.
    *   *Example*: "I see you just read an email from Alice about the Q3 report. Do you want me to open the Q3 Excel file?"
*   **How**: Track active window focus history and clipboard content to build a predictive context model.
