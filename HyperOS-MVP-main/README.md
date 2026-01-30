# HyperOS-MVP 🚀

**HyperOS-MVP** is an autonomous AI desktop agent designed to perform complex tasks by interacting with your computer exactly like a human would. It uses a sophisticated **ANALYZE → PLAN → EXECUTE** loop powered by **Mistral AI (Pixtral)**.

## 🧠 Core Architecture: The 3-Step Cycle

HyperOS doesn't just "guess" what to do next. It follows a strict cognitive loop for every single action:

1.  **ANALYZE (Vision Context)**:
    *   Captures a real-time screenshot of your desktop.
    *   Uses **Pixtral's** multimodal capabilities to identify UI elements (buttons, text fields, icons).
    *   Understands the current system state (which windows are open, what's focused).

2.  **PLAN (Strategy & Logic)**:
    *   Breaks down the user's high-level task into micro-steps.
    *   Reasoning is attached to every planned action (e.g., "I need to click the Start button to find Notepad").
    *   Dynamically adapts if an unexpected window pops up or an action fails.

3.  **EXECUTE (Physical Automation)**:
    *   Translates AI plans into real system commands.
    *   Uses **PyAutoGUI** to physically move the mouse, click elements, and type text.
    *   Includes safety delays to ensure the OS has time to process the inputs.

---

## ✨ Features

*   **Autonomous Operation**: Give it a task like "Open Chrome and find the latest AI news," and watch it work.
*   **Mistral Pixtral Integration**: State-of-the-art vision and reasoning model.
*   **Premium Glassmorphic UI**: A futuristic, always-on-top Electron overlay that visualizes the agent's internal thought process.
*   **Real-time Visualization**: See exactly what the AI is "Thinking," "Planning," and "Doing" with color-coded step tracking.
*   **Global Hotkey**: Press `Ctrl+Space` to quickly summon or hide the agent.

## 🛠️ Technology Stack

*   **AI Engine**: Mistral AI (Pixtral-12B)
*   **Backend**: Python (FastAPI)
*   **Frontend**: React, TailwindCSS, Lucide-Icons
*   **Runtime**: Electron (for the sleek desktop overlay)
*   **Automation**: PyAutoGUI

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js & npm
*   Mistral API Key (from [Mistral Console](https://console.mistral.ai/))

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/HyperOS-MVP.git
    cd HyperOS-MVP
    ```
2.  **Set Up API Key**:
    *   Navigate to `agent-core/`
    *   Create a `.env` file and add:
        ```env
        MISTRAL_API_KEY=your_mistral_api_key_here
        ```
3.  **Install Dependencies**:
    ```bash
    # For the agent core
    cd agent-core
    pip install -r requirements.txt
    
    # For the UI
    cd ..
    npm install
    ```

### Running HyperOS
Simply run the boot script in the root directory:
```powershell
./start.bat
```

---

## 📂 Project Structure

*   `agent-core/`: The Python logic, AI model integration, and automation engine.
*   `electron/`: Main and preload scripts for the transparent overlay window.
*   `src/`: React frontend source code for the premium UI.
*   `start.bat`: One-click startup script for both backend and frontend.

---

## 🛡️ Safety Note
This agent has the power to control your mouse and keyboard. Always supervise the agent during task execution. You can stop the process anytime by closing the terminal or using the `Ctrl+C` command.

*Developed by Antigravity (Advanced Agentic AI)*
