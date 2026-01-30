"""
HyperOS Demo Script
Test the agent with simple tasks
"""
from agent import HyperOSAgent
import time

def run_demo():
    print("=" * 60)
    print("HyperOS Demo - Testing Desktop Automation")
    print("=" * 60)
    print()
    
    # Initialize agent
    print("Initializing HyperOS Agent...")
    agent = HyperOSAgent()
    print("✓ Agent initialized")
    print()
    
    # Demo tasks
    demo_tasks = [
        "Open Notepad",
        "Type 'Hello from HyperOS!'",
        "Save the file as test.txt on Desktop"
    ]
    
    print("Demo Tasks:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"  {i}. {task}")
    print()
    
    input("Press Enter to start demo (make sure your desktop is visible)...")
    print()
    
    # Execute each task
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n[Task {i}/{len(demo_tasks)}] {task}")
        print("-" * 60)
        
        result = agent.execute_task(task)
        
        print(f"\nResult: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Steps taken: {result.get('steps', 'N/A')}")
        
        if result['status'] != 'success':
            print("\n⚠️ Task failed or incomplete. Stopping demo.")
            break
        
        # Wait between tasks
        if i < len(demo_tasks):
            print("\nWaiting 3 seconds before next task...")
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. MISTRAL_API_KEY is set in .env file")
        print("2. All dependencies are installed (pip install -r requirements.txt)")
        print("3. Tesseract OCR is installed")
