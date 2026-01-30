import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import pygetwindow as gw
from PIL import Image, ImageTk, ImageGrab
import time
import keyboard
import os
import subprocess
import json
from datetime import datetime

# --- HYPEROS PRO AGENT: AGENTIC BRAIN + VISION + EXECUTION ---

class VisionSystem:
    @staticmethod
    def identify_active_window():
        try:
            return gw.getActiveWindow().title
        except:
            return "Unknown"

    @staticmethod
    def locate_window(name):
        wins = gw.getWindowsWithTitle(name)
        return wins[0] if wins else None

class AgentBrain:
    def __init__(self, log_fn):
        self.log = log_fn

    def create_plan(self, task):
        self.log("👁️ VISION: Scanning desktop surface...")
        time.sleep(0.8)
        active_window = VisionSystem.identify_active_window()
        self.log(f"🧠 CONTEXT: Current focus is '{active_window}'.")
        
        self.log(f"🧠 ANALYZING TASK: '{task}'")
        time.sleep(1.0)
        
        t = task.lower()
        plan = []

        if "notepad" in t:
            self.log("💡 STRATEGY: Resource 'Notepad' required. Orchestrating launch and text injection sequence.")
            plan = [
                {"type": "LOG", "msg": "Strategic Goal: Initialize Notepad and deploy content."},
                {"type": "EXEC", "cmd": "start notepad", "desc": "Triggering system process: notepad.exe"},
                {"type": "WAIT", "sec": 2, "desc": "Synchronizing with application lifecycle..."},
                {"type": "VISION", "target": "Notepad", "desc": "Vision Verification: Locating software interface"},
                {"type": "TYPE", "text": t.split("type")[-1] if "type" in t else "Hello World from HyperOS", "desc": "Autonomous Data Entry: Typing sequence active"}
            ]
        elif "calc" in t:
            self.log("💡 STRATEGY: Mathematical engine requested. Path: System Calculator.")
            plan = [
                {"type": "LOG", "msg": "Strategic Goal: Compute values via native app."},
                {"type": "EXEC", "cmd": "start calc", "desc": "Spawning Calculator process..."},
                {"type": "WAIT", "sec": 1.5},
                {"type": "VISION", "target": "Calculator", "desc": "Vision Focus: Locking on calculator UI"}
            ]
        elif "chrome" in t or "google" in t:
            self.log("💡 LOGIC: Browser request. Strategy: Launch default web client + navigation.")
            plan = [
                {"type": "EXEC", "cmd": "start chrome", "desc": "Booting Google Chrome..."},
                {"type": "WAIT", "sec": 3},
                {"type": "TYPE", "text": "https://google.com\n", "desc": "Automating URI navigation"}
            ]
        else:
            self.log(f"💡 LOGIC: Complex task detected. Using heuristic execution for '{task}'")
            plan = [{"type": "EXEC", "cmd": f"start {task}", "desc": f"Attempting to launch {task}"}]

        self.log(f"📋 STRATEGIC PLAN READY ({len(plan)} Actions)")
        return plan

class ActionEngine:
    def __init__(self, log_fn, outline_fn):
        self.log = log_fn
        self.outline = outline_fn

    def execute_action(self, action):
        atype = action.get('type')
        desc = action.get('desc', 'Executing...')

        if atype != "LOG":
            self.log(f"▶️ RUNNING: {desc}")

        if atype == "EXEC":
            # Direct execution for common apps
            cmd = action['cmd']
            if "notepad" in cmd.lower():
                subprocess.Popen(['notepad.exe'])
            elif "calc" in cmd.lower():
                subprocess.Popen(['calc.exe'])
            else:
                subprocess.Popen(cmd, shell=True)
        elif atype == "WAIT":
            time.sleep(action['sec'])
        elif atype == "VISION":
            win = VisionSystem.locate_window(action['target'])
            if win:
                self.log(f"✨ VISION CONFIRMED: Found '{win.title}'")
                self.outline(win.left, win.top, win.width, win.height, f"AGENT FOCUS: {action['target']}")
                try: 
                    win.activate()
                    win.maximize()
                    time.sleep(1.0)
                    # Force focus by clicking center of the window area
                    pyautogui.click(win.left + (win.width // 2), win.top + (win.height // 2))
                except: pass
            else:
                self.log(f"⚠️ VISION WARNING: Could not find '{action['target']}'")
        elif atype == "TYPE":
            pyautogui.write(action['text'], interval=0.08)
        elif atype == "LOG":
            self.log(f"📄 STATUS: {action['msg']}")

class HyperOSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        # Global Overlay
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-alpha', 0.8, '-topmost', True, '-transparentcolor', 'black')
        self.overlay.geometry(f"{sw}x{sh}+0+0")
        self.canvas = tk.Canvas(self.overlay, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.glow = self.canvas.create_rectangle(15, 15, sw-15, sh-15, outline='#0080FF', width=30, state='hidden')

        # Chat Overlay
        self.chat = tk.Toplevel(self.root)
        self.chat.overrideredirect(True)
        self.chat.attributes('-topmost', True)
        self.chat.configure(bg='#020617')
        self.chat.geometry(f"440x650+{(sw-480)}+{(sh-750)}")
        self.frame = tk.Frame(self.chat, bg='#020617', highlightbackground='#0080FF', highlightthickness=2)
        self.frame.pack(fill='both', expand=True)

        self.setup_ui()
        self.chat.bind('<Button-1>', self.start_drag)
        self.chat.bind('<B1-Motion>', self.do_drag)
        keyboard.add_hotkey('ctrl+space', self.toggle)

        self.brain = AgentBrain(self.log)
        self.engine = ActionEngine(self.log, self.mark_ui)

    def setup_ui(self):
        h = tk.Frame(self.frame, bg='#1e293b', height=50)
        h.pack(fill='x')
        tk.Label(h, text="● HYPEROS AGENT CORE", bg='#1e293b', fg='#38bdf8', font=('Segoe UI Bold', 10)).pack(side='left', padx=15)
        
        self.history = tk.Text(self.frame, bg='#020617', fg='#cbd5e1', font=('Consolas', 9), state='disabled', borderwidth=0, padx=20, pady=25, wrap='word')
        self.history.pack(fill='both', expand=True)
        
        self.entry = tk.Entry(self.frame, bg='#0f172a', fg='white', borderwidth=0, font=('Segoe UI', 11), insertbackground='#38bdf8')
        self.entry.pack(fill='x', padx=20, pady=20, ipady=15)
        self.entry.bind('<Return>', self.on_task)
        self.entry.focus_set()

    def log(self, text):
        self.history.config(state='normal')
        self.history.insert('end', f"{text}\n\n")
        self.history.config(state='disabled')
        self.history.see('end')

    def mark_ui(self, x, y, w, h, label):
        self.canvas.create_rectangle(x, y, x+w, y+h, outline='#0080FF', width=4, tags='vision')
        self.canvas.create_text(x, y-20, text=label, fill='#0080FF', font=('Arial', 10, 'bold'), anchor='nw', tags='vision')
        self.root.after(4000, lambda: self.canvas.delete('vision'))

    def on_task(self, e=None):
        task = self.entry.get().strip()
        if not task: return
        self.entry.delete(0, 'end')
        self.log(f"User Request: {task}")
        self.canvas.itemconfigure(self.glow, state='normal')
        
        def run_thread():
            plan = self.brain.create_plan(task)
            for action in plan:
                self.engine.execute_action(action)
                time.sleep(0.4)
            self.log("🏁 AGENT: Task completed successfully.")
            self.canvas.itemconfigure(self.glow, state='hidden')

        threading.Thread(target=run_thread, daemon=True).start()

    def toggle(self):
        if self.chat.winfo_viewable():
            self.chat.withdraw()
            self.overlay.withdraw()
        else:
            self.chat.deiconify()
            self.overlay.deiconify()
            self.chat.lift()

    def start_drag(self, e):
        self.dx = e.x
        self.dy = e.y

    def do_drag(self, e):
        nx = self.chat.winfo_x() + (e.x - self.dx)
        ny = self.chat.winfo_y() + (e.y - self.dy)
        self.chat.geometry(f"+{nx}+{ny}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HyperOSApp()
    app.run()
