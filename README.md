# AI-counter
# 🎟️ TicketAI – Natural Language-Based Ticket Booking

TicketAI is a simple AI assistant that helps users book travel tickets using natural language input instead of manually filling forms or navigating websites.

---

## ✅ What It Does

- Accepts human input like:  
  _"Book a ticket for Preeti from Delhi to Hyderabad on 13th Feb. Her phone number is 3456."_

- Extracts details (name, phone number, source, destination, date) using a language model (Mistral 7B via Hugging Face API)

- Sends the booking to a backend API that stores it in an SQLite database

- Runs on a local Flask server with a clean web interface

---

## 🚀 Features

- LLM-powered text interpretation
- Simple, form-free booking via chat
- Flask-based local server
- SQLite-backed ticket storage
- Hugging Face API integration

---


## 📌 Use Case

Designed for users who prefer booking tickets via simple, conversational input without navigating through traditional UIs.
-----------------------------

## 🛠️ Setup

TicketAI Setup Instructions
---------------------------

1. Clone the repository:
   git clone https://github.com/himanshudas13/AI-counter.git
   cd your-repo-name

2. (Optional) Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate       # On Windows: venv\Scripts\activate

3. Install required packages:
   pip install -r requirements.txt

4. Get a Hugging Face API token:
   - Visit https://huggingface.co/settings/tokens
   - Generate a token with "inference" permission

5. Create a `.env` file in the root directory and add:
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
   BOOKING_API_URL=http://127.0.0.1:5000/book

6. Run the server:
   python server.py

7. Open your browser and go to:
   http://127.0.0.1:5000

8. Use the chat interface to book tickets using plain English input.

Example:
   "Book a ticket for Preeti from Delhi to Hyderabad on 13th Feb. Phone number is 3456."

That's it — you're ready to book tickets using natural language input.


---

