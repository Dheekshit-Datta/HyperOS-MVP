# 🚀 HyperOS - Desktop AI Agent with Mistral AI

**A Claude Cowork clone that ACTUALLY automates your desktop using Mistral Pixtral vision model**

## 🎯 What is HyperOS?

HyperOS is a desktop automation agent that:
- ✅ **Takes real screenshots** of your desktop
- ✅ **Analyzes them using Mistral Pixtral** (vision AI model)
- ✅ **Executes REAL mouse clicks and keyboard actions** via PyAutoGUI
- ✅ **Runs in an analyze-plan-execute loop** just like Claude Cowork

## 📁 File Structure

```
hyperos/
├── main.py                 # Main application entry point
├── agent.py               # Core agent loop (analyze-plan-execute)
├── screen_capture.py      # Screenshot capture functions
├── action_executor.py     # PyAutoGUI automation commands
├── mistral_api.py         # Mistral API integration (NOT Claude)
├── ui_overlay.py          # Tkinter chat overlay UI
├── element_detector.py    # OCR and UI element detection
├── config.py              # API keys and settings
└── requirements.txt       # Python dependencies
```

## 🔧 Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (usually `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or set in code:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 3: Set Mistral API Key

Get your API key from: https://console.mistral.ai/

**Windows (PowerShell):**
```powershell
$env:MISTRAL_API_KEY="your-mistral-api-key-here"
```

**Mac/Linux:**
```bash
export MISTRAL_API_KEY="your-mistral-api-key-here"
```

Or edit `config.py` directly:
```python
MISTRAL_API_KEY = "your-mistral-api-key-here"
```

## 🚀 How to Run

```bash
python main.py
```

This will:
1. Launch a floating chat window (always on top)
2. Initialize the HyperOS agent with Mistral Pixtral
3. Wait for your commands

## 💬 Example Usage

**In the chat window, type:**

```
Open Notepad and type Hello World
```

**What happens:**
1. 📸 Agent takes screenshot
2. 🔍 OCR detects UI elements
3. 🤖 Mistral Pixtral analyzes the screen
4. 💡 Mistral decides: "Click Start button at (20, 800)"
5. ⚡ PyAutoGUI executes: `pyautogui.click(20, 800)`
6. 🔄 Loop continues until task is complete

## 🧠 How It Works (Mistral API Flow)

```
User: "Open Calculator"
    ↓
[1] ANALYZE
    → screen_capture.py takes screenshot
    → element_detector.py runs OCR
    ↓
[2] PLAN
    → mistral_api.py sends screenshot to Pixtral
    → Mistral responds: {"action": {"type": "click", "x": 50, "y": 750}}
    ↓
[3] EXECUTE
    → action_executor.py runs: pyautogui.click(50, 750)
    → REAL CLICK happens on your desktop
    ↓
[4] VERIFY
    → Takes new screenshot
    → Checks if action succeeded
    ↓
[LOOP] Repeat until task complete
```

## 🎮 Available Actions

The agent can perform:

- **click**: Click at coordinates
  ```json
  {"type": "click", "x": 100, "y": 200, "target": "Start button"}
  ```

- **type**: Type text
  ```json
  {"type": "type", "text": "Hello World"}
  ```

- **press_key**: Press keyboard key
  ```json
  {"type": "press_key", "key": "enter"}
  ```

- **hotkey**: Press key combination
  ```json
  {"type": "hotkey", "keys": ["ctrl", "c"]}
  ```

- **wait**: Wait for UI to load
  ```json
  {"type": "wait", "seconds": 2}
  ```

- **task_complete**: Mark task as done
  ```json
  {"type": "task_complete", "message": "Successfully opened Notepad"}
  ```

## 🔐 Safety Features

- **PyAutoGUI Failsafe**: Move mouse to top-left corner to emergency stop
- **Max Steps**: Limited to 50 steps per task (configurable in `config.py`)
- **Pause Between Actions**: 0.5s delay for safety

## 🐛 Troubleshooting

### "Mistral API error"
- Check your API key is set correctly
- Verify you have credits in your Mistral account
- Check internet connection

### "OCR detection failed"
- Make sure Tesseract is installed
- Verify Tesseract is in your PATH
- On Windows, set the path manually in `element_detector.py`

### "No module named 'mistralai'"
- Run: `pip install mistralai`
- Make sure you're using the correct Python environment

### Actions not executing
- Check PyAutoGUI is installed: `pip install pyautogui`
- On Linux, you may need: `sudo apt-get install python3-tk python3-dev`

## 🆚 HyperOS vs Claude Cowork

| Feature | Claude Cowork | HyperOS |
|---------|--------------|---------|
| Vision Model | Claude 3.5 Sonnet | Mistral Pixtral 12B |
| API Provider | Anthropic | Mistral AI |
| Automation | PyAutoGUI | PyAutoGUI |
| Architecture | Analyze-Plan-Execute | Analyze-Plan-Execute |
| UI | Electron | Tkinter |
| Cost | Higher (Claude API) | Lower (Mistral API) |

## 📊 System Requirements

- **Python**: 3.8+
- **OS**: Windows, Mac, or Linux
- **RAM**: 4GB minimum
- **Internet**: Required for Mistral API calls

## 🔑 API Costs

Mistral Pixtral pricing (as of 2024):
- Input: ~$0.15 per 1M tokens
- Output: ~$0.15 per 1M tokens

Each screenshot + analysis ≈ 1000-2000 tokens
Estimated cost: **$0.0003 per action** (very cheap!)

## 🎯 Example Tasks

Try these commands:

```
1. "Open Notepad and type Hello World"
2. "Open Calculator and calculate 5 + 3"
3. "Open Chrome and go to google.com"
4. "Create a new folder on Desktop called Test"
5. "Open File Explorer and navigate to Documents"
```

## 🚨 Important Notes

1. **This ACTUALLY controls your mouse/keyboard** - don't run untrusted tasks
2. **Keep the chat window visible** - it stays on top for monitoring
3. **Emergency stop**: Move mouse to top-left corner
4. **First run may be slow** - Mistral API cold start

## 📝 License

MIT License - Use freely, modify as needed

## 🤝 Contributing

This is a clone of Claude Cowork but using Mistral AI. Feel free to:
- Add more action types
- Improve OCR detection
- Enhance the UI
- Add voice control
- Integrate with other AI models

## 🎉 Credits

- Inspired by **Claude Cowork** (Anthropic)
- Powered by **Mistral Pixtral** vision model
- Built with **PyAutoGUI** for automation
- Uses **Tesseract OCR** for element detection

---

**Made with ❤️ for desktop automation enthusiasts**
