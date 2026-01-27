import mss
import mss.tools

def capture_all():
    with mss.mss() as sct:
        # Loop through all detected monitors
        # Start at 1 because 0 is the "All Screens Combined" view
        for i, monitor in enumerate(sct.monitors):
            if i == 0: continue 

            print(f"📸 Capturing Monitor {i} ({monitor['width']}x{monitor['height']})...")
            
            output_filename = f"monitor_{i}.png"
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_filename)
            
            print(f"   ✅ Saved {output_filename}")

if __name__ == "__main__":
    capture_all()
