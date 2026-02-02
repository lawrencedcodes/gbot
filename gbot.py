import os
import time
import json
import traceback
import pyautogui
import mss
import mss.tools
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
load_dotenv()
# Note: Ensure your .env has GOOGLE_API_KEY (The Robot Key)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY") or 'service-account.json'

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- GEMINI SETUP ---
if not GOOGLE_API_KEY:
    print("❌ ERROR: No GOOGLE_API_KEY found. Check your .env file.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

# 🧠 THE V2 BRAIN: Supports CLICK, TYPE, and KEY PRESS
SYSTEM_PROMPT = """
You are G-Bot, an autonomous GUI agent.
You control a mouse and keyboard on a computer monitor.
The user will give you a text command and a screenshot.

You must reply with pure JSON only. No markdown. No chatter.
Your response must follow one of these formats:

1. TO CLICK:
{
    "action": "click",
    "x": <integer_x_coordinate>,
    "y": <integer_y_coordinate>,
    "rationale": "Brief reason for clicking here"
}

2. TO TYPE (only if a text field is ALREADY focused or you just clicked one):
{
    "action": "type",
    "text": "the text to type",
    "rationale": "Brief reason for typing"
}

3. TO PRESS A KEY (e.g., enter, esc, backspace):
{
    "action": "key",
    "key": "enter",
    "rationale": "Submitting the form"
}

CRITICAL RULES:
- The screen width is based on the provided image.
- Return ONLY valid JSON.
"""

# Using 'gemini-1.5-flash' for speed, or switch to 'gemini-2.0-flash' if available
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

def capture_ghost_monitor():
    with mss.mss() as sct:
        monitors = sct.monitors
        if len(monitors) < 2:
            print("❌ Error: No secondary monitor detected!")
            return None, None
        
        # ✅ FIX: Automatically grab the LAST monitor in the list (The Ghost)
        ghost_monitor = monitors[-1] 
        
        screenshot = sct.grab(ghost_monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # 📸 DEBUG: Save vision to check what the bot sees
        img.save("debug_view.png")
        print("📸 Debug: Saved vision to 'debug_view.png'")
        
        return img, ghost_monitor

def execute_action(action_data, monitor_offset_x, monitor_offset_y):
    """Executes the JSON instruction from Gemini."""
    action_type = action_data.get("action")
    rationale = action_data.get("rationale", "No rationale")

    print(f"🤖 ACTION: {action_type.upper()} | {rationale}")

    if action_type == "click":
        local_x = action_data.get("x")
        local_y = action_data.get("y")
        
        if local_x is None or local_y is None:
            print("❌ Error: Missing coordinates for click.")
            return

        # Convert to Global Desktop Coordinates
        global_x = monitor_offset_x + local_x
        global_y = monitor_offset_y + local_y

        # 🛡️ SAFETY CHECK: Ensure we are not clicking on the main screen (assuming Ghost is to the right)
        # You can adjust this logic based on your specific setup
        if global_x < monitor_offset_x:
             print(f"🛡️ BLOCKED: Attempted to click outside Ghost Monitor (X={global_x})")
             return

        print(f"   🖱️ Moving to ({global_x}, {global_y})")
        pyautogui.moveTo(global_x, global_y, duration=0.5)
        pyautogui.click()
    
    elif action_type == "type":
        text_to_type = action_data.get("text", "")
        print(f"   ⌨️ Typing: '{text_to_type}'")
        pyautogui.write(text_to_type, interval=0.05)

    elif action_type == "key":
        key_name = action_data.get("key", "")
        print(f"   🎹 Pressing Key: {key_name}")
        pyautogui.press(key_name)

def process_command(command_text, doc_ref):
    print(f"\n📨 Received: '{command_text}'")
    
    # 1. Capture Vision
    screen_img, monitor_info = capture_ghost_monitor()
    if not screen_img:
        doc_ref.update({"status": "error", "error": "Monitor not found"})
        return

    # 2. Consult the Brain
    print("🧠 Thinking...")
    try:
        response = model.generate_content([command_text, screen_img])
        
        # Clean up response
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        print(f"   🔍 AI Output: {clean_text}") # Debug print
        
        action_data = json.loads(clean_text)

        # 3. Execute Hands
        execute_action(action_data, monitor_info["left"], monitor_info["top"])

        # 4. Mark Complete
        doc_ref.update({
            "status": "completed",
            "response": f"Executed: {action_data.get('rationale', 'Action done')}",
            "processedAt": datetime.now()
        })
        print("✅ Command Complete.")

    except Exception as e:
        print(f"💥 Error: {e}")
        traceback.print_exc()
        doc_ref.update({"status": "error", "error": str(e)})

def listen_loop():
    print("🤖 G-BOT V2 (THE TYPIST) ONLINE. Waiting for commands...")
    print("   (Check 'debug_view.png' to see what the bot sees)")
    
    # Listen to 'commands' collection
    commands_ref = db.collection("commands")
    query = commands_ref.where("status", "==", "pending")

    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == "ADDED":
                data = change.document.to_dict()
                cmd_text = data.get("text")
                if cmd_text:
                    process_command(cmd_text, change.document.reference)

    query.on_snapshot(on_snapshot)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        listen_loop()
    except KeyboardInterrupt:
        print("\n💤 G-Bot sleeping.")