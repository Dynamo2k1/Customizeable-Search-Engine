from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from auth import auth_blueprint
from search import search_blueprint
from database import db
from models import Favorite  # Import the Favorite model here

# Initialize the Flask app
app = Flask(__name__)

# App configuration
app.config["SECRET_KEY"] = "12358289247" 
app.config["SESSION_TYPE"] = "filesystem"  
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://dynamo:1590@localhost/search_engine"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and session
db.init_app(app)
Session(app)

# Register Blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(search_blueprint, url_prefix="/search")

# Routes
@app.route("/")
def home():
    # Redirect to the search page for displaying the home page with the search form
    return redirect(url_for("search.search_page"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/favorites")
def favorites():
    if "user_id" not in session:
        flash("You must be logged in to view your favorites.", "warning")
        return redirect(url_for("auth.login"))

    # Fetch the user's favorite items from the database
    user_id = session["user_id"]
    favorites = db.session.query(Favorite).filter_by(user_id=user_id).all()
    return render_template("favorites.html", favorites=favorites)


@app.route("/logout")
def logout():
    # Clears the user session and redirects to the home page
    session.pop("user_id", None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
