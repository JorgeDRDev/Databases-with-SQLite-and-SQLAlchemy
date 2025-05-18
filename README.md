📚 Book Collection Manager
A simple yet robust Flask web app to manage your personal library. Add, view, update, and delete
books with ease—complete with input validation, error handling, and a clean SQLite backend.

🚀 Features
📖 Add new books with title, author, and rating

✏️ Edit book ratings inline

❌ Delete books securely

🔍 View all books sorted alphabetically

🧠 Validates input and handles edge cases

💥 Graceful error handling with user-friendly flash messages

🧱 Powered by Flask, SQLAlchemy, and SQLite

🛠 Tech Stack
Flask – Lightweight Python web framework

SQLAlchemy – ORM for database interactions

SQLite – Embedded relational database

HTML – Clean, responsive UI

🗂 Project Structure
bash
Copy
Edit
├── templates/
│   ├── index.html
│   ├── add.html
│   └── edit_rating.html
├── books-collection.db
├── app.py
├── README.md
🧪 Running Locally
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/book-collection-manager.git
cd book-collection-manager
Set up a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install Flask SQLAlchemy
Run the app:

bash
Copy
Edit
python app.py
Then open http://127.0.0.1:5000 in your browser.

📌 Notes
Default database is books-collection.db (SQLite).

Ratings must be between 0 and 10.

Titles must be unique; duplicate titles will raise a warning.

🧠 Future Improvements
Search/filter functionality

User authentication

Pagination for large libraries

API endpoint for external access

🪪 License
MIT License. Use it, hack it, improve it—just don’t pretend you wrote it if you didn’t.
