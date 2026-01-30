import tkinter as tk
from tkinter import ttk
import threading
import requests
import json

class HyperOSOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HyperOS Agent")
        
        # Transparent Overlay Settings
        self.root.attributes('-alpha', 0.9) # Semi-transparent
        self.root.attributes('-topmost', True) # Always on top
        self.root.overrideredirect(True) # Frameless
        
        # Position on right side
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 400
        height = 600
        x = screen_width - width - 50
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # UI Styling
        self.style = ttk.Style()
        self.root.configure(bg="#0a0a0a")
        
        # Header
        self.header = tk.Frame(self.root, bg="#0080FF", height=40)
        self.header.pack(fill="x")
        self.title_label = tk.Label(self.header, text="HYPEROS AGENT", fg="white", bg="#0080FF", font=("Arial", 10, "bold"))
        self.title_label.pack(side="left", padx=10, pady=10)
        
        self.close_btn = tk.Label(self.header, text="X", fg="white", bg="#0080FF", font=("Arial", 10, "bold"), cursor="hand2")
        self.close_btn.pack(side="right", padx=10)
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # Chat Area
        self.chat_area = tk.Text(self.root, bg="#111111", fg="#cccccc", font=("Segoe UI", 10), state="disabled", wrap="word", borderwidth=0, highlightthickness=0)
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Input Area
        self.input_frame = tk.Frame(self.root, bg="#111111")
        self.input_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        self.input_entry = tk.Entry(self.input_frame, bg="#222222", fg="white", insertbackground="white", borderwidth=0, font=("Segoe UI", 11))
        self.input_entry.pack(fill="x", ipady=8)
        self.input_entry.bind("<Return>", self.send_command)
        
        self.root.bind("<Control-Space>", self.toggle_visibility)
        
        self.log_message("SYSTEM: Connected to Desktop core.")
        self.log_message("SYSTEM: HyperOS is ready natively.")

    def log_message(self, msg):
        self.chat_area.config(state="normal")
        self.chat_area.insert("end", f"{msg}\n\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see("end")

    def send_command(self, event=None):
        cmd = self.input_entry.get()
        if not cmd: return
        self.input_entry.delete(0, "end")
        self.log_message(f"YOU: {cmd}")
        
        # Simulate agent processing
        threading.Thread(target=self.process_command, args=(cmd,), daemon=True).start()

    def process_command(self, cmd):
        try:
            # Here we would call the agent core
            # For this demo, just mock a response
            import time
            time.sleep(1)
            self.log_message(f"AGENT: I am executing '{cmd}' on your desktop.")
            if "screen" in cmd.lower():
                 self.log_message("AGENT: [MOCK] Drawing blue outlines over UI elements...")
        except Exception as e:
            self.log_message(f"ERROR: {e}")

    def toggle_visibility(self, event=None):
        if self.root.winfo_viewable():
            self.root.withdraw()
        else:
            self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    overlay = HyperOSOverlay()
    overlay.run()
