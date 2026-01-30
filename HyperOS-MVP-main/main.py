"""
HyperOS - Desktop AI Agent (Cowork clone with Mistral)
Main entry point
"""
import sys
from agent import HyperOSAgent
from ui_overlay import launch_chat_ui

def main():
    print("🚀 HyperOS Starting...")
    
    # Initialize agent
    agent = HyperOSAgent()
    
    # Launch chat overlay UI
    launch_chat_ui(agent)
    
if __name__ == "__main__":
    main()
