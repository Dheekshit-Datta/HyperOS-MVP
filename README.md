# HyperOS - Desktop Agentic Assistant

HyperOS is an autonomous desktop AI agent that can see your screen, control your mouse/keyboard, and perform tasks through natural language commands.

## Core Capabilities
- **Visual Understanding**: Continuously capture and analyze screenshots.
- **Desktop Control**: Mouse/Keyboard control via OS-level APIs.
- **Agent Intelligence**: Breaks down complex requests into steps (Planning, Self-Correction).
- **Task Execution**: File management, Web browsing, App control.

## Technical Architecture
- **Frontend**: Electron + React + Vite + TailwindCSS (for a premium, dynamic UI).
- **Backend/Agent**: Python (FastAPI + PyAutoGUI + LangChain/OpenAI).
- **Communication**: HTTP/WebSocket between Electron (UI) and Python (Agent).
- **AI Models**: Designed to support OpenAI (GPT-4o), Claude 3.5 Sonnet (Computer Use), or Local LLMs.

## Project Structure
- `/src`: Electron main and renderer processes.
- `/agent-core`: Python based agent logic (Vision, Planning, Action).
- `/resources`: Assets.

## Getting Started
1. Install Node.js dependencies: `npm install`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run Development Mode: `npm run dev`
