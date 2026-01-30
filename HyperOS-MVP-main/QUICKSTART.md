# 🚀 HyperOS Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Dependencies (2 minutes)

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (2 minutes)

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer
- Add to PATH or edit `element_detector.py` line 13:
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

### 3. Get Mistral API Key (1 minute)

1. Go to: https://console.mistral.ai/
2. Sign up / Log in
3. Create API key
4. Copy the key

### 4. Configure API Key

**Option A: Environment Variable (Recommended)**

Create `.env` file:
```bash
MISTRAL_API_KEY=your-actual-api-key-here
```

**Option B: Direct in config.py**

Edit `config.py`:
```python
MISTRAL_API_KEY = "your-actual-api-key-here"
```

### 5. Run HyperOS! 🎉

```bash
python main.py
```

A chat window will appear. Try:
```
Open Notepad and type Hello World
```

---

## 🎮 Quick Test

Run the demo script:
```bash
python demo.py
```

This will automatically:
1. Open Notepad
2. Type "Hello from HyperOS!"
3. Save file to Desktop

---

## 🐛 Common Issues

### "No module named 'mistralai'"
```bash
pip install mistralai
```

### "Mistral API error: 401"
- Check your API key is correct
- Make sure you have credits in your Mistral account

### "pytesseract.TesseractNotFoundError"
- Tesseract not installed or not in PATH
- See step 2 above

### "ImportError: No module named 'tkinter'"
**Linux:**
```bash
sudo apt-get install python3-tk
```

### Actions not executing
- Make sure you're running Python 3.8+
- Check PyAutoGUI is installed: `pip list | grep pyautogui`

---

## 📊 What Happens When You Run It?

```
1. Chat window opens (stays on top)
   ↓
2. You type: "Open Calculator"
   ↓
3. Agent takes screenshot
   ↓
4. Sends to Mistral Pixtral API
   ↓
5. Mistral analyzes and responds:
   {"action": {"type": "click", "x": 50, "y": 750}}
   ↓
6. PyAutoGUI executes: pyautogui.click(50, 750)
   ↓
7. REAL CLICK happens on your screen!
   ↓
8. Loop continues until task complete
```

---

## 🎯 Try These Commands

```
✅ "Open Notepad"
✅ "Open Calculator and calculate 5 + 3"
✅ "Open File Explorer"
✅ "Create a new folder on Desktop called Test"
✅ "Open Chrome and go to google.com"
✅ "Minimize all windows"
```

---

## 🚨 Safety Tips

1. **Emergency Stop**: Move mouse to top-left corner
2. **Watch the agent**: Keep chat window visible
3. **Start simple**: Test with "Open Notepad" first
4. **Don't leave unattended**: This controls your computer!

---

## 💰 API Costs

Mistral Pixtral is VERY cheap:
- ~$0.0003 per action
- 1000 actions ≈ $0.30

Much cheaper than Claude API!

---

## 📚 Next Steps

1. ✅ Run `python main.py`
2. ✅ Test with simple task
3. ✅ Try more complex tasks
4. ✅ Read full README_HYPEROS.md
5. ✅ Customize for your needs

---

## 🤝 Need Help?

Check the full documentation: `README_HYPEROS.md`

---

**You're ready to go! 🚀**

Run `python main.py` and start automating!
