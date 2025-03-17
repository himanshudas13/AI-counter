from flask import Flask, send_from_directory, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__, template_folder='.', static_folder='.')  # Treat the "web" folder as root

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
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        if not data['name'] or not data['phone'] or not data['from'] or not data['to'] or not data['date']:
         return jsonify({"error": "Missing required fields"}), 400
     
        c.execute("INSERT INTO tickets (name, phone, from_city, to_city, date) VALUES (?, ?, ?, ?, ?)", 
                  (data['name'], data['phone'], data['from'], data['to'], data['date']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Ticket booked successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
