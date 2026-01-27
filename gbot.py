import firebase_admin
from firebase_admin import credentials, firestore
import mss
import mss.tools
import pyautogui
import time
import os

# --- CONFIGURATION ---
CRED_FILE = 'service-account.json'

# --- 1. SETUP FIREBASE ---
cred = credentials.Certificate(CRED_FILE)
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# --- 2. THE BODY (GHOST DRIVER) ---
def get_ghost_monitor_id(sct):
    """Auto-detects the right-most monitor (The Ghost)"""
    ghost_id = -1
    max_left = -99999
    
    for i, monitor in enumerate(sct.monitors):
        if i == 0: continue # Skip 'All Combined'
        if monitor["left"] > max_left:
            max_left = monitor["left"]
            ghost_id = i
    return ghost_id

def execute_ghost_action(action_name):
    """
    This is where the robot actually moves.
    For now, we just perform a 'Check' action (Screenshot + Center Mouse).
    """
    print(f"👻 GHOST ACTING: Performing '{action_name}'...")
    
    with mss.mss() as sct:
        # A. Find the Ghost
        ghost_id = get_ghost_monitor_id(sct)
        if ghost_id == -1:
            return "❌ Error: Ghost Monitor not found!"

        monitor = sct.monitors[ghost_id]
        
        # B. Move Mouse to Center of Ghost Screen
        center_x = monitor["left"] + (monitor["width"] // 2)
        center_y = monitor["top"] + (monitor["height"] // 2)
        
        print(f"   🖱️  Moving to Ghost Center ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=0.5)
        
        # C. Take Proof of Life Screenshot
        output_file = "ghost_action_proof.png"
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_file)
        
        return f"✅ Action '{action_name}' executed on Monitor {ghost_id}. Proof saved to {output_file}."

# --- 3. THE NERVOUS SYSTEM (LISTENER) ---
def on_command(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
            doc_id = change.document.id
            
            if data.get('status') == 'pending':
                print(f"\n📨 TRIGGER: {data.get('action')}")
                
                # EXECUTE THE BODY
                result = execute_ghost_action(data.get('action'))
                
                # REPORT BACK TO CLOUD
                db.collection('commands').document(doc_id).update({
                    'status': 'completed',
                    'response': result
                })
                print("   📡 Cloud updated.")

def main():
    print("🤖 G-BOT ONLINE. Watching for Firestore commands...")
    
    # Listen to 'commands' collection
    query = db.collection('commands').where('status', '==', 'pending')
    query.on_snapshot(on_command)
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
