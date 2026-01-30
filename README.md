eact PWA):** A secure, mobile-first command deck where the human operator issues natural language directives ("Clean up this folder", "Sort these PDFs").
2.  **The Nervous System (Firebase):** Handles real-time synchronization of commands and enforces strict biometric authentication (Google Auth).
3.  **The Body (Python & Gemini):**
    * **Vision:** Captures screenshots of the virtual display using `mss`.
    * **Brain:** Sends visual data to **Google Gemini 1.5 Flash** to identify UI elements and extract coordinates.
    * **Hands:** Converts relative coordinates to global desktop space and executes input via `pyautogui`.

---

## 🛡 Security: The "Glass Box" Protocol

G-Bot is designed with a "Security First" approach to autonomous agents.

* **Visual I# 👻 G-BOT: Autonomous Visual Desktop Agent

> **"A ghost in the machine."**

G-Bot is an experimental AI agent that lives on a virtual secondary display (the "Ghost Monitor"). It perceives the operating system purely through computer vision, analyzes the UI using Multimodal LLMs (Google Gemini), and executes physical input actions (mouse/keyboard) to perform tasks.

Unlike traditional agents that hook into OS APIs or run on your main screen, G-Bot is architected as a **"Virus in a Glass Box."** It is sandboxed within a virtual display, unable to interact with sensitive files or the main desktop unless they are explicitly dragged into its environment.

---

## 🏗 System Architecture

The system operates on a **Trinity Architecture**:

1.  **The Remote solation:** G-Bot runs on a dedicated virtual monitor (created via BetterDisplay or similar).
* **Coordinate Hard-Lock:** The mouse driver is hard-coded to reject any coordinates `X < 0` (or outside the virtual monitor bounds). It physically cannot click on your main Start Menu, Terminal, or Password Manager.
* **Human Intent Firewall:** The agent can only manipulate windows and files that the user intentionally drags into the "Ghost Monitor."
* **Mute by Default:** (V1) The agent currently has no keyboard access, eliminating the risk of shell command injection.

---

## 🚀 Features

### ✅ V1: The Pointer (Current)
* **Remote Control:** Send commands from any device via the React Web App.
* **Visual Target Acquisition:** Can identify icons, buttons, and windows by name or description ("Click the blue folder").
* **Multi-Monitor Support:** Translates local screenshot coordinates to global macOS desktop coordinates.

### 🚧 V2: The Typist (In Progress)
* **Keyboard Support:** Secure text entry for renaming files or searching within sandboxed windows.
* **Input Sanitization:** Blocks dangerous keystrokes (e.g., `Cmd+Space`, `Return` in terminal contexts).

### 🔮 V3: The Automaton (Planned)
* **Looping Logic:** Ability to perform multi-step tasks ("Move all screenshots to the Images folder").
* **Visual Verification:** Using Agentic Vision to "zoom and enhance" before clicking to prevent false positives.

---

## 🛠 Installation & Setup

### Prerequisites
* Python 3.10+
* Node.js & npm
* Google Cloud Project (Gemini API)
* Firebase Project (Firestore & Auth)

### 1. The Body (Python Backend)
```bash
# Clone the repo
git clone [https://github.com/yourusername/gbot.git](https://github.com/yourusername/gbot.git)
cd gbot

# Create Virtual Environment
python -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Configure Environment
# Create a .env file and add:
# GOOGLE_API_KEY=your_gemini_key
# SERVICE_ACCOUNT

cd client

# Install Dependencies
npm install

# Configure Environment
# Create a .env file in /client and add your Firebase public keys:
# VITE_API_KEY=...
# VITE_AUTH_DOMAIN=...

🎮 Usage
Wake the Ghost: Run the Python agent on your host machine.

Bash
python gbot.py
Open the Remote: Launch the web interface (Local or Deployed).

Bash
cd client && npm run dev
Command: Log in via Google Auth and type a command:

"Click on the window named 'Nothing Folder'."

⚠️ Disclaimer
Use with caution. While G-Bot is sandboxed, giving an AI control over your mouse implies inherent risks. The "Glass Box" coordinate limits are a software governor, not a hardware switch. Always monitor the agent during operation.
