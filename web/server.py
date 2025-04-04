from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import os
import sys


# Ensure the path includes the correct directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web.api import MyTravels
from agent.llm import TicketAI  # Ensure `agent/llm.py` exists

app = Flask(__name__, template_folder='.', static_folder='.') # Treat the "web" folder as root

# Initialize database
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tickets 
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, from_city TEXT, to_city TEXT, date TEXT)''')
    conn.commit()
    conn.close()

# Serve index.html
@app.route('/')
def home():
    return render_template('index.html')

# Serve style.css
@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')  # Serving CSS from the same directory

# Handle ticket booking
@app.route('/book', methods=['POST'])
def book_ticket():
    try:
        data = request.json

        # Validate required fields
        if not data.get('name') or not data.get('phone') or not data.get('from') or not data.get('to') or not data.get('date'):
            return jsonify({"error": "Missing required fields"}), 400

        # Safe SQLite connection with thread support
        with sqlite3.connect("bookings.db", check_same_thread=False) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO tickets (name, phone, from_city, to_city, date) 
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['name'], data['phone'], data['from'], data['to'], data['date']
            ))
            conn.commit()

        return jsonify({"message": "Ticket booked successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    agent = TicketAI()
    response = agent.call_agent(user_input)  # Capture output from call_agent

    return jsonify({"response": response})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
