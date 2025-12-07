# synxai/__init__.py
import os
from flask import Flask
import google.generativeai as genai
import sqlite3

# ------------------------------------------------------------------
# Create Flask app + write HTML/CSS files on first import
# ------------------------------------------------------------------
def _create_template_and_static():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static", "css")

    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    # ---- index.html ------------------------------------------------
    index_path = os.path.join(templates_dir, "index.html")
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(INDEX_HTML)
        print("Created synxai/templates/index.html")

    # ---- style.css -------------------------------------------------
    css_path = os.path.join(static_dir, "style.css")
    if not os.path.exists(css_path):
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(STYLE_CSS)
        print("Created synxai/static/css/style.css")

# ------------------------------------------------------------------
# Your full Flask app (exactly as you had, but inside the package)
# ------------------------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

def configure_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')  # or gemini-2.5-flash when available

configure_api_key()
model = initialize_model()

def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'chats.db'))
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
with get_db_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (thread_id) REFERENCES threads (id)
        )
    ''')

@app.route('/')
def index():
    return app.send_static_file('../../templates/index.html') if not os.path.exists('templates/index.html') else app.send_static_file('index.html')
    # Fallback for both packaged and dev mode

# === Your original routes (unchanged) ===
from .app import *  # imports all routes defined in app.py

# ------------------------------------------------------------------
# Embedded files as strings (so no external files needed)
# ------------------------------------------------------------------
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyberpunk Chatbot</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@400;700&family=Roboto+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/night-owl.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <style>
        /* All your beautiful inline styles go here (same as before) */
        /* ... (paste your entire <style> block from index.html) ... */
    </style>
</head>
<body>
    <!-- Your full HTML body (exactly as you posted) -->
    <div class="container">
        <div class="sidebar" id="sidebar">
            <h2>Threads</h2>
            <div class="sidebar-item" id="new-thread">+ New Thread</div>
        </div>
        <div class="chat-container">
            <div class="messages" id="messages"></div>
            <div class="typing" id="typing"></div>
            <div class="suggestions" id="suggestions">
                <button class="suggestion-btn">What's the weather in San Francisco?</button>
                <button class="suggestion-btn">Explain React hooks like useState and useEffect</button>
            </div>
            <div class="input-area">
                <input type="text" id="message-input" placeholder="Send a message...">
                <button id="send-btn">Send</button>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.18/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        // Your entire JS (same as you posted) goes here
        // ... (all your JavaScript code)
    </script>
</body>
</html>"""

STYLE_CSS = """
/* Paste the entire content of your style.css here */
/* (All the cyberpunk CSS you already have) */
"""

# ------------------------------------------------------------------
# Auto-create files on import
# ------------------------------------------------------------------
_create_template_and_static()

# Optional: run with `python -m synxai`
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)