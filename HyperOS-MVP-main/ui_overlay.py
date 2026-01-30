"""
Chat UI overlay - floating chat window on desktop
"""
import tkinter as tk
from tkinter import scrolledtext
import threading

class ChatOverlay:
    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("HyperOS")
        self.root.geometry("400x600")
        self.root.attributes('-topmost', True)  # Always on top
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=50,
            height=30,
            state='disabled'
        )
        self.chat_display.pack(padx=10, pady=10)
        
        # Input field
        self.input_field = tk.Entry(self.root, width=50)
        self.input_field.pack(padx=10, pady=5)
        self.input_field.bind('<Return>', self.send_message)
        
        # Send button
        self.send_button = tk.Button(
            self.root,
            text="Send",
            command=self.send_message
        )
        self.send_button.pack(pady=5)
        
    def send_message(self, event=None):
        task = self.input_field.get()
        if task:
            self.add_message(f"You: {task}")
            self.input_field.delete(0, tk.END)
            
            # Execute task in background thread
            thread = threading.Thread(
                target=self.execute_task_thread,
                args=(task,)
            )
            thread.start()
    
    def execute_task_thread(self, task):
        self.add_message("HyperOS: Executing task...")
        result = self.agent.execute_task(task)
        self.add_message(f"HyperOS: {result['message']}")
    
    def add_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def run(self):
        self.root.mainloop()

def launch_chat_ui(agent):
    overlay = ChatOverlay(agent)
    overlay.run()
