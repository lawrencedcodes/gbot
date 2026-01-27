import mss
import pyautogui

def scout_monitors():
    print("🕵️ SCOUTING DISPLAYS...")
    
    with mss.mss() as sct:
        # List all monitors. 
        # monitors[0] is usually "All combined", [1] is Main, [2] is Ghost.
        for i, monitor in enumerate(sct.monitors):
            print(f"\n🖥️  Monitor {i}:")
            print(f"   Top: {monitor['top']}, Left: {monitor['left']}")
            print(f"   Width: {monitor['width']}, Height: {monitor['height']}")
            
            if i == 2:
                print("   (🎯 This should be your Ghost Display)")

    print("\n---------------------------------------------------")
    print("🖱️  CURRENT MOUSE POSITION:")
    print(pyautogui.position())
    print("---------------------------------------------------")

if __name__ == "__main__":
    scout_monitors(


)
