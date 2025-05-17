from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from sqlalchemy import exc as sqlalchemy_exc

app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
# Configure a secret key for session management (e.g., for flashing messages)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_me'

db = SQLAlchemy()
db.init_app(app)

class Book(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}, Rating: {self.rating}>'


# This needs to be done within an application context.
with app.app_context():
    db.create_all()


# Display all books
@app.route('/')
def home():
    try:
        # Query all books from the database, ordered by title
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars().all()
    except sqlalchemy_exc.SQLAlchemyError as e:
        # Log the error (in a real app, use proper logging)
        print(f"Database error on home route: {e}")
        flash("Could not retrieve books from the database.", "danger")
        all_books = []
    return render_template("index.html", books=all_books)


# Add book
@app.route("/add", methods=["GET", "POST"])
def add():
    form_data = {
        "title": request.form.get("title", ""),
        "author": request.form.get("author", ""),
        "rating_str": request.form.get("rating", "")
    }

    if request.method == "POST":
        title = form_data["title"]
        author = form_data["author"]
        rating_str = form_data["rating_str"]

        error_found = False
        if not title:
            flash("Book title is required.", "warning")
            error_found = True
        if not author:
            flash("Book author is required.", "warning")
            error_found = True
        if not rating_str:
            flash("Book rating is required.", "warning")
            error_found = True

        rating = None
        if rating_str:
            try:
                rating = float(rating_str)
                if not (0 <= rating <= 10):
                    flash("Rating must be a number between 0 and 10.", "warning")
                    error_found = True
            except ValueError:
                flash("Invalid rating. Please enter a number (e.g., 8.5).", "danger")
                error_found = True

        if error_found:
            return render_template("add.html", form_data=form_data)

        new_book = Book(title=title, author=author, rating=rating)

        try:
            db.session.add(new_book)
            db.session.commit()
            flash(f"Book '{title}' added successfully!", "success")
            return redirect(url_for('home'))
        except sqlalchemy_exc.IntegrityError:
            db.session.rollback()  # Important to roll back the session
            flash(f"Error: A book with the title '{title}' already exists. Please choose a different title.", "danger")
        except sqlalchemy_exc.SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error on add route: {e}")
            flash("An unexpected error occurred while adding the book. Please try again.", "danger")

        return render_template("add.html", form_data=form_data)

    return render_template("add.html", form_data=form_data)


# Edit book's rating
@app.route("/edit-rating/<int:book_id>", methods=["GET", "POST"])
def edit_rating(book_id):
    book_to_update = db.get_or_404(Book, book_id)  # More concise way to get a book or 404

    if request.method == "POST":
        new_rating_str = request.form.get("rating")
        if not new_rating_str:
            flash("Rating is required.", "warning")
            return render_template("edit_rating.html", book=book_to_update)

        try:
            new_rating = float(new_rating_str)
            if not (0 <= new_rating <= 10):
                flash("Rating must be between 0 and 10.", "warning")
                return render_template("edit_rating.html", book=book_to_update)
        except ValueError:
            flash("Invalid rating format.", "danger")
            return render_template("edit_rating.html", book=book_to_update)

        try:
            book_to_update.rating = new_rating
            db.session.commit()
            flash(f"Rating for '{book_to_update.title}' updated successfully!", "success")
            return redirect(url_for('home'))
        except sqlalchemy_exc.SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error on edit_rating route: {e}")
            flash("An error occurred while updating the rating.", "danger")
            return render_template("edit_rating.html", book=book_to_update)

    return render_template("edit_rating.html", book=book_to_update)


# Delete book
@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    book_to_delete = db.get_or_404(Book, book_id)
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        flash(f"Book '{book_to_delete.title}' deleted successfully.", "success")
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error on delete_book route: {e}")
        flash("An error occurred while deleting the book.", "danger")
    return redirect(url_for('home'))


# To run the application (optional, can be run with 'flask run' command)
if __name__ == "__main__":
    app.run(debug=True)

    # # Create dummy HTML files if they don't exist for basic testing
    # import os
    #
    # templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    # if not os.path.exists(templates_dir):
    #     os.makedirs(templates_dir)
    #
    # index_html_path = os.path.join(templates_dir, "index.html")
    # add_html_path = os.path.join(templates_dir, "add.html")
    # edit_rating_html_path = os.path.join(templates_dir, "edit_rating.html")


#     app.run(debug=True)
# ```html
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>My Book Collection</title>
#     <style>
#         body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; color: #333; }
#         h1 { color: #444; text-align: center; }
#         ul { list-style-type: none; padding: 0; }
#         li { background-color: #fff; border: 1px solid #eee; margin-bottom: 10px; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
#         .actions a { margin-left: 12px; text-decoration: none; padding: 6px 10px; border-radius: 4px; font-size: 0.9em; }
#         .actions a.edit { background-color: #ffc107; color: #333; }
#         .actions a.delete { background-color: #dc3545; color: white; }
#         .flash { padding: 12px 15px; margin-bottom: 18px; border-radius: 5px; font-size: 0.95em; }
#         .flash.success { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
#         .flash.danger { background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }
#         .flash.warning { background-color: #fff3cd; color: #664d03; border: 1px solid #ffecb5; }
#         a { color: #007bff; text-decoration: none; }
#         a:hover { text-decoration: underline; }
#         .container { max-width: 850px; margin: 20px auto; background: #ffffff; padding: 25px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-radius: 8px; }
#         .add-book-link { display: inline-block; margin-bottom: 25px; padding: 12px 18px; background-color: #198754; color: white; border-radius: 5px; text-decoration: none; font-size: 1.05em; }
#         .add-book-link:hover { background-color: #157347; }
#         .no-books { text-align: center; color: #666; font-size: 1.1em; padding: 20px; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h1>My Book Collection</h1>
#
#         {% with messages = get_flashed_messages(with_categories=true) %}
#             {% if messages %}
#                 {% for category, message in messages %}
#                     <div class="flash {{ category }}">{{ message }}</div>
#                 {% endfor %}
#             {% endif %}
#         {% endwith %}
#
#         <a href="{{ url_for('add') }}" class="add-book-link">Add New Book</a>
#
#         {% if not books %}
#             <p class="no-books">No books found in the collection yet. Why not add one?</p>
#         {% else %}
#             <ul>
#                 {% for book in books %}
#                 <li>
#                     <span>
#                         <strong>{{ book.title }}</strong> by {{ book.author }} - Rating: {{ book.rating }}/10
#                     </span>
#                     <span class="actions">
#                         <a href="{{ url_for('edit_rating', book_id=book.id) }}" class="edit">Edit Rating</a>
#                         <a href="{{ url_for('delete_book', book_id=book.id) }}" class="delete" onclick="return confirm('Are you sure you want to delete the book \'{{ book.title|escapejs }}\'?');">Delete</a>
#                     </span>
#                 </li>
#                 {% endfor %}
#             </ul>
#         {% endif %}
#     </div>
# </body>
# </html>
