from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from auth import auth_blueprint
from search import search_blueprint
from database import db

# Initialize the Flask app
app = Flask(__name__)

# App configuration
app.config["SECRET_KEY"] = "12358289247"  # Replace with a secure key
app.config["SESSION_TYPE"] = "filesystem"  # For managing user sessions
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
    if "user_id" in session:
        return redirect(url_for("search.search_page"))
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
