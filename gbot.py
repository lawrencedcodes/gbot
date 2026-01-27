import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import mss
import mss.tools
import pyautogui
import time
import os
import json
from dotenv import load_dotenv
from PIL import Image

# --- CONFIGURATION ---
load_dotenv()
CRED_FILE = 'service-account.json'
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- SETUP AI ---
if not API_KEY:
    print("❌ ERROR: No GOOGLE_API_KEY found in .env")
    exit()

genai.configure(api_key=API_KEY)
# Using the stable model that worked for you
model = genai.GenerativeModel('gemini-2.5-flash')

# --- SETUP FIREBASE ---
cred = credentials.Certificate(CRED_FILE)
app = firebase_admin.initialize_app(cred)
db = firestore.client()

def get_ghost_monitor_id(sct):
    """Auto-detects the right-most monitor (The Ghost)"""
    ghost_id = -1
    max_left = -99999
    
    for i, monitor in enumerate(sct.monitors):
        if i == 0: continue
        if monitor["left"] > max_left:
            max_left = monitor["left"]
            ghost_id = i
    return ghost_id

def analyze_and_click(target_description):
    print(f"🧠 THINKING: Looking for '{target_description}'...")
    
    with mss.mss() as sct:
        # 1. Capture Ghost Screen
        ghost_id = get_ghost_monitor_id(sct)
        if ghost_id == -1: return "❌ Error: Ghost Monitor not found!"

        monitor = sct.monitors[ghost_id]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # 2. Ask Gemini for Coordinates
        prompt = f"""
        Look at this screenshot. I need to click on: "{target_description}".
        Return ONLY a JSON object with the coordinates.
        Format: {{ "x": <int>, "y": <int> }}
        If not found, return {{ "error": "not found" }}
        """
        
        try:
            response = model.generate_content([prompt, img])
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
        except Exception as e:
            return f"❌ AI Error: {e}"

        if "error" in data:
            return f"❌ Could not find '{target_description}' on screen."

        # 3. COORDINATE MATH (The most important part)
        # Gemini gives coordinates relative to the screenshot (0,0 is top-left of Ghost)
        # We need Global Coordinates (0,0 is top-left of Main Screen)
        
        local_x = data['x']
        local_y = data['y']
        
        global_x = monitor["left"] + local_x
        global_y = monitor["top"] + local_y
        
        print(f"   🎯 TARGET ACQUIRED: Local({local_x},{local_y}) -> Global({global_x},{global_y})")
        
        # 4. EXECUTE
        pyautogui.moveTo(global_x, global_y, duration=0.7)
        pyautogui.click()
        
        return f"✅ Clicked '{target_description}' at ({global_x}, {global_y})"

# --- THE LISTENER LOOP ---
def on_command(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
            doc_id = change.document.id
            
            if data.get('status') == 'pending':
                action = data.get('action')
                print(f"\n📨 COMMAND: {action}")
                
                # Run the Vision Agent
                result = analyze_and_click(action)
                print(f"   {result}")
                
                # Report back to Cloud
                db.collection('commands').document(doc_id).update({
                    'status': 'completed',
                    'response': result
                })

def main():
    print("🤖 G-BOT V1 ONLINE. Connected to Nervous System & Vision Center.")
    print("   Waiting for orders...")
    
    query = db.collection('commands').where('status', '==', 'pending')
    query.on_snapshot(on_command)
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
