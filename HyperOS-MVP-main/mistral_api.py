"""
Mistral API integration - sends screenshots and gets next action
Uses Pixtral vision model for screenshot analysis
"""
from mistralai import Mistral
import base64
import json
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

def ask_mistral_what_to_do(task, screenshot, elements, conversation_history):
    """
    Send screenshot to Mistral Pixtral and ask what action to take next
    This is the BRAIN of HyperOS - using Mistral instead of Claude
    """
    
    # Convert screenshot to base64
    screenshot_base64 = image_to_base64(screenshot)
    
    # Build conversation messages for Mistral
    messages = []
    
    # Add conversation history (previous screenshots and actions)
    for history_item in conversation_history[-5:]:  # Last 5 steps
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{image_to_base64(history_item['screenshot'])}"
                },
                {
                    "type": "text",
                    "text": f"Previous action: {json.dumps(history_item['action'])}"
                }
            ]
        })
        messages.append({
            "role": "assistant",
            "content": f"Action executed: {json.dumps(history_item['result'])}"
        })
    
    # Add current screenshot and task
    prompt_text = f"""
You are HyperOS, a desktop automation agent. You can see the user's desktop screenshot.

TASK: {task}

DETECTED UI ELEMENTS ON SCREEN:
{json.dumps(elements, indent=2)}

Analyze the screenshot and decide the NEXT action to take to complete this task.

You can perform these actions:
- click: Click at coordinates {{"type": "click", "x": 100, "y": 200, "target": "element name"}}
- type: Type text {{"type": "type", "text": "hello"}}
- press_key: Press keyboard key {{"type": "press_key", "key": "enter"}}
- hotkey: Press key combination {{"type": "hotkey", "keys": ["ctrl", "c"]}}
- wait: Wait for UI to load {{"type": "wait", "seconds": 2}}
- task_complete: Task is done {{"type": "task_complete", "message": "Success description"}}

Respond in JSON format ONLY (no markdown, no backticks):
{{
  "reasoning": "explain what you see and why you're taking this action",
  "action": {{
    "type": "click",
    "x": 100,
    "y": 200,
    "target": "element name"
  }}
}}

Think step by step:
1. What do you see on the screen right now?
2. What is the current state?
3. What is the next step to complete the task?
4. What action should you take?

Respond ONLY with valid JSON.
"""
    
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{screenshot_base64}"
            },
            {
                "type": "text",
                "text": prompt_text
            }
        ]
    })
    
    # Call Mistral Pixtral API
    try:
        response = client.chat.complete(
            model="pixtral-12b-2409",  # Mistral's vision model
            messages=messages,
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse response
        response_text = response.choices[0].message.content
        
        # Clean up response (remove markdown if present)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        parsed_response = json.loads(response_text)
        
        return parsed_response
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse Mistral response: {response_text}")
        print(f"Error: {e}")
        return {
            "reasoning": "Failed to parse response, waiting...",
            "action": {"type": "wait", "seconds": 1}
        }
    except Exception as e:
        print(f"❌ Mistral API error: {e}")
        return {
            "reasoning": f"API error: {str(e)}",
            "action": {"type": "wait", "seconds": 2}
        }

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
