import os
import google.generativeai as genai
import mss
import mss.tools
import json
from dotenv import load_dotenv

# 1. Load Environment Variables
# Create a .env file with: GOOGLE_API_KEY=your_key_here
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found. Please set it in a .env file.")
    exit()

genai.configure(api_key=api_key)

# 2. Configure the Model
# We use 'gemini-2.0-flash-exp' (or 'gemini-1.5-flash' if 2.0 isn't available to you yet)
model = genai.GenerativeModel('gemini-2.5-flash') 

def get_ghost_monitor_id(sct):
    """Reuse our detector logic"""
    max_left = -99999
    ghost_id = -1
    for i, monitor in enumerate(sct.monitors):
        if i == 0: continue
        if monitor["left"] > max_left:
            max_left = monitor["left"]
            ghost_id = i
    return ghost_id

def analyze_ghost_screen(prompt_instruction):
    print(f"🧠 THINKING: Analyzing Ghost Screen for '{prompt_instruction}'...")
    
    with mss.mss() as sct:
        # A. Capture
        ghost_id = get_ghost_monitor_id(sct)
        monitor = sct.monitors[ghost_id]
        sct_img = sct.grab(monitor)
        output_debug = "brain_debug.png"
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_debug)
        print(f"   📸 Debug: Saved what the bot sees to '{output_debug}'")
        # Convert to PIL Image (Gemini loves PIL)
        from PIL import Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # B. Prompt Engineering
        # We ask for JSON coordinates specifically
        full_prompt = f"""
        Look at this desktop screenshot. 
        I need to click on the UI element described as: "{prompt_instruction}".
        
        Return ONLY a JSON object with the coordinates. 
        Format: {{ "x": <integer>, "y": <integer>, "confidence": <float> }}
        
        The coordinates should be roughly the center of the element.
        If you cannot find it, return {{ "error": "not found" }}
        """
        
        # C. Call Gemini
        response = model.generate_content([full_prompt, img])
        
        # D. Parse
        try:
            # Strip potential markdown code blocks
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            print(f"   💡 GEMINI SAYS: {data}")
            return data, monitor # Return monitor too so we can calculate global offset
        except Exception as e:
            print(f"   ❌ ERROR Parsing Gemini: {e}")
            print(f"   Raw Response: {response.text}")
            return None, None

if __name__ == "__main__":
    # TEST RUN
    # Make sure you have something visible on the Ghost screen (e.g., drag a folder there)
    # Then try to find it.
    analyze_ghost_screen("Window named nothing folder")
