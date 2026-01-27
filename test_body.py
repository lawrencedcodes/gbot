import mss
import pyautogui
import time

def get_ghost_monitor_id(sct):
    """
    Auto-detects the Ghost Monitor.
    Strategy: Find the monitor with the largest 'left' coordinate 
    (the one furthest to the right).
    """
    ghost_id = -1
    max_left = -99999
    
    # Start at 1 to skip the "All Monitors" combined view (Index 0)
    for i, monitor in enumerate(sct.monitors):
        if i == 0: continue
        
        # Look for the one furthest to the right
        if monitor["left"] > max_left:
            max_left = monitor["left"]
            ghost_id = i
            
    return ghost_id

def test_ghost():
    print("👻 G-BOT ACTIVATING...")
    
    with mss.mss() as sct:
        # 1. Auto-Detect the ID
        GHOST_ID = get_ghost_monitor_id(sct)
        
        # Safety Check: Did we find it?
        if GHOST_ID == -1 or len(sct.monitors) <= GHOST_ID:
            print("❌ ERROR: Could not find the Ghost Monitor!")
            print(f"   Monitors found: {len(sct.monitors)-1}")
            print("   👉 Check if BetterDisplay is running.")
            return

        monitor = sct.monitors[GHOST_ID]
        print(f"✅ LOCKED ONTO MONITOR {GHOST_ID} (Left: {monitor['left']})")

        # 2. Calculate Center
        center_x = monitor["left"] + (monitor["width"] // 2)
        center_y = monitor["top"] + (monitor["height"] // 2)
        
        # 3. Capture Evidence
        print(f"📸 CAPTURING Monitor {GHOST_ID}...")
        output = "ghost_view.png"
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)
        print(f"   Saved to {output}")
        
        # 4. Move the Mouse
        print(f"🖱️ MOVING mouse to: ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=1.0)
        print("✅ Movement complete.")

if __name__ == "__main__":
    test_ghost()
