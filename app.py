from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

def configure_api_key():
    """Configure the Google Generative AI API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

def initialize_model():
    """Initialize the Generative AI model."""
    try:
        # Using gemini-2.5-flash model; replace with desired model if needed
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model
    except Exception as e:
        raise RuntimeError(f"Error initializing model: {e}")

# Configure API key and model at startup
configure_api_key()
model = initialize_model()

# Database connection
def get_db_connection():
    conn = sqlite3.connect('chats.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
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
    """Serve the HTML UI."""
    return render_template('index.html')

@app.route('/threads', methods=['GET'])
def get_threads():
    """Get list of threads."""
    conn = get_db_connection()
    threads = conn.execute('SELECT * FROM threads ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in threads])

@app.route('/threads', methods=['POST'])
def create_thread():
    """Create a new thread."""
    data = request.get_json()
    title = data.get('title', 'New Thread')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO threads (title) VALUES (?)', (title,))
    thread_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': thread_id, 'title': title})

@app.route('/messages/<int:thread_id>', methods=['GET'])
def get_messages(thread_id):
    """Get messages for a thread."""
    conn = get_db_connection()
    messages = conn.execute('SELECT role, content FROM messages WHERE thread_id = ? ORDER BY timestamp ASC', (thread_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in messages])

@app.route('/chat/<int:thread_id>', methods=['POST'])
def chat(thread_id):
    """Handle chat messages and return AI response for a specific thread."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Store user message
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)',
                     (thread_id, 'user', user_message))
        conn.commit()
        
        # Generate AI response
        response = model.generate_content(user_message)
        
        # Store bot response
        bot_response = response.text
        conn.execute('INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)',
                     (thread_id, 'bot', bot_response))
        conn.commit()
        conn.close()
        
        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'error': f'Error generating response: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
