# HyperOS - Vision-Enabled AI Desktop Agent

<div align="center">

![HyperOS Logo](docs/assets/logo-placeholder.png)

**The "Iron Man JARVIS" for your desktop** - An AI agent that sees your screen and automates tasks through natural language.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Electron](https://img.shields.io/badge/electron-28-9cf.svg)](https://www.electronjs.org/)

</div>

---

## 🚀 What is HyperOS?

HyperOS is a **vision-enabled desktop AI agent** that:

- 👁️ **Sees** - Captures and analyzes your screen using Gemini 1.5 Flash Vision AI
- 🧠 **Thinks** - Plans multi-step workflows to complete your tasks  
- 🎯 **Acts** - Executes mouse clicks, keyboard inputs, and application control

Unlike chatbots trapped in a browser, HyperOS operates as a transparent overlay on your desktop, automating real work across any application.

---

## 📸 Screenshots

> Add screenshots here after running the application:
> - `docs/assets/screenshot-idle.png` - Main overlay interface
> - `docs/assets/screenshot-executing.png` - Agent executing a task
> - `docs/assets/screenshot-steps.png` - Step visualization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HyperOS Architecture                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │   User Input     │───▶│  Electron Shell  │───▶│  React UI     │ │
│  │  (Ctrl+Space)    │    │  (Transparent)   │    │  (Overlay)    │ │
│  └──────────────────┘    └──────────────────┘    └───────┬───────┘ │
│                                                          │          │
│                                                          ▼          │
│                                               ┌──────────────────┐  │
│                                               │  FastAPI Server  │  │
│                                               │   (Port 8000)    │  │
│                                               └────────┬─────────┘  │
│                                                        │            │
│                          ┌─────────────────────────────┼──────────┐ │
│                          │                             │          │ │
│                          ▼                             ▼          │ │
│               ┌──────────────────┐          ┌──────────────────┐  │ │
│               │  Screen Capture  │          │  Gemini 1.5 AI   │  │ │
│               │   (pyautogui)    │─────────▶│  Vision Analysis │  │ │
│               └──────────────────┘          └────────┬─────────┘  │ │
│                                                      │            │ │
│                                                      ▼            │ │
│                                           ┌──────────────────┐    │ │
│                                           │  Action Engine   │    │ │
│                                           │  (Mouse/Keyboard)│    │ │
│                                           └──────────────────┘    │ │
│                          └────────────────────────────────────────┘ │
│                                    Python Agent Core                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://python.org/downloads)
- **Node.js 18+** - [Download](https://nodejs.org)
- **Gemini API Key** - [Get Free Key](https://makersuite.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HyperOS-MVP.git
   cd HyperOS-MVP
   ```

2. **Configure your API key**
   ```bash
   # Copy the example config
   cp agent-core/.env.example agent-core/.env
   
   # Edit and add your Gemini API key
   # GEMINI_API_KEY=your_key_here
   ```

3. **Start HyperOS**
   
   **Windows:**
   ```batch
   start.bat
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. **Use the overlay**
   - Press `Ctrl+Space` to toggle the overlay
   - Type a task like "Open Notepad and type Hello World"
   - Watch the AI analyze, plan, and execute!

---

## 🎮 Usage

### Global Hotkey

| Shortcut | Action |
|----------|--------|
| `Ctrl+Space` | Toggle overlay visibility |

### Example Tasks

```
"Open Chrome and search for weather"
"Open Calculator and compute 25 * 17"
"Open Notepad and type a poem about AI"
"Click the Start button"
"Press Alt+Tab to switch windows"
```

### Available Actions

The AI can perform these actions:

| Action | Description | Example |
|--------|-------------|---------|
| `click` | Click at coordinates | `click(500, 300)` |
| `type` | Type text | `type("Hello World")` |
| `press_key` | Press keyboard key | `press_key("enter")` |
| `wait` | Wait for UI | `wait(2)` |
| `done` | Mark task complete | `done("Task finished")` |

---

## 🛠️ Development

### Manual Setup

**Backend:**
```bash
cd agent-core
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
npm install
npm run dev
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run electron:dev` | Start with Electron |
| `npm run build` | Build for production |
| `npm run electron:build` | Build Electron app |

### Running Tests

```bash
# Python tests
cd agent-core
python -m pytest tests/ -v

# TypeScript type checking
npm run typecheck
```

---

## 📁 Project Structure

```
HyperOS-MVP/
├── agent-core/              # 🐍 Python backend
│   ├── agent.py             # Main HyperOSAgent class
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Configuration (create from .env.example)
│   ├── tools/
│   │   └── window_manager.py
│   └── tests/
│       └── test_agent_core.py
│
├── electron/                # ⚡ Electron shell
│   ├── main.ts              # Main process
│   ├── preload.ts           # IPC bridge
│   └── tsconfig.json
│
├── src/                     # ⚛️ React frontend
│   ├── App.tsx              # Main UI component
│   ├── main.tsx             # Entry point
│   ├── index.css            # TailwindCSS styles
│   └── vite-env.d.ts
│
├── docs/                    # 📚 Documentation
│   ├── API.md               # API reference
│   └── ARCHITECTURE.md      # System design
│
├── package.json             # Node dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind customization
├── electron-builder.yml     # Build configuration
├── start.bat                # Windows launcher
├── start.sh                 # Linux/macOS launcher
└── README.md                # You are here!
```

---

## 🔧 Configuration

### Environment Variables

Create `agent-core/.env` with:

```env
# Required: Your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Backend port (default: 8000)
# PORT=8000
```

### Customization

- **UI Position**: Edit `src/App.tsx` - modify `right-6 top-1/2` classes
- **Max Steps**: Edit `agent-core/agent.py` - change `MAX_STEPS = 20`
- **Step Delay**: Edit `agent-core/agent.py` - change `STEP_DELAY = 1.0`

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "GEMINI_API_KEY not found" | Create `.env` file in `agent-core/` with your API key |
| Backend won't start | Check if port 8000 is in use: `netstat -ano \| findstr 8000` |
| Overlay not appearing | Press `Ctrl+Space` - check if Electron started |
| Clicks are inaccurate | Gemini may hallucinate coordinates - try simpler tasks |
| Python not found | Ensure Python is in PATH: `python --version` |
| npm install fails | Delete `node_modules/` and `package-lock.json`, retry |

### Debug Mode

Enable verbose logging:

```python
# In agent-core/agent.py, change:
logging.basicConfig(level=logging.DEBUG, ...)
```

### Check Backend Health

```bash
curl http://127.0.0.1:8000/
# Should return: {"status": "HyperOS Agent Active", ...}
```

---

## 🔒 Security Considerations

> ⚠️ **Warning**: HyperOS can execute arbitrary mouse/keyboard actions on your system.

- Never run HyperOS with untrusted tasks
- The agent can see sensitive information on screen
- API keys are stored locally in `.env` (gitignored)
- No data is logged to external servers

---

## 🗺️ Roadmap

### v1.1 (Current)
- ✅ Gemini 1.5 Flash vision integration
- ✅ Basic action execution (click, type, press_key)
- ✅ Transparent Electron overlay
- ✅ Cancel task support

### v2.0 (Planned)
- ⬜ Windows UI Automation (pywinauto) for reliable clicking
- ⬜ Local RAG with ChromaDB for document context
- ⬜ Voice input support
- ⬜ Multi-monitor support
- ⬜ Persistent memory between sessions

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Google Gemini](https://deepmind.google/technologies/gemini/) for vision AI
- [Electron](https://www.electronjs.org/) for desktop shell
- [FastAPI](https://fastapi.tiangolo.com/) for backend framework
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for automation

---

<div align="center">

**Built with ❤️ by Antigravity**

[Report Bug](https://github.com/yourusername/HyperOS-MVP/issues) · [Request Feature](https://github.com/yourusername/HyperOS-MVP/issues)

</div>
