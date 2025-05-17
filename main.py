from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from sqlalchemy import exc as sqlalchemy_exc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
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


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    try:
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars().all()
    except sqlalchemy_exc.SQLAlchemyError as e:
        print(f"Database error on home route: {e}")
        flash("Could not retrieve books from the database.", "danger")
        all_books = []
    return render_template("index.html", books=all_books)


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
            db.session.rollback()
            flash(f"Error: A book with the title '{title}' already exists. Please choose a different title.", "danger")
        except sqlalchemy_exc.SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error on add route: {e}")
            flash("An unexpected error occurred while adding the book. Please try again.", "danger")

        return render_template("add.html", form_data=form_data)

    return render_template("add.html", form_data=form_data)


@app.route("/edit-rating/<int:book_id>", methods=["GET", "POST"])
def edit_rating(book_id):
    book_to_update = db.get_or_404(Book, book_id)

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


if __name__ == "__main__":
    app.run(debug=True)