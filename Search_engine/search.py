from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from database import db
from models import SearchHistory
from utils import perform_web_scraping_with_categories
from json import dumps

search_blueprint = Blueprint("search", __name__)

API_KEY = "AIzaSyBiXTEPooZiuotBUXaipIoMZCCiOFOiUc4"
CX = "b213191287aba4aef"

@search_blueprint.route("/search", methods=["GET", "POST"])
def search_page():
    if "user_id" not in session:
        flash("You must be logged in to access the search page.", "warning")
        return redirect(url_for("auth.login"))

    search_results = []
    if request.method == "POST":
        query = request.form.get("query")
        category = request.form.get("category")

        if not query or not category:
            flash("Both search query and category are required.", "danger")
            return redirect(url_for("search.search_page"))

        # Perform web scraping using the updated function
        search_results = perform_web_scraping_with_categories(query, category, API_KEY, CX)

        # Save search history in the database
        user_id = session["user_id"]
        history_entry = SearchHistory(user_id=user_id, query=query, results=search_results)
        db.session.add(history_entry)
        db.session.commit()

        flash("Search completed successfully!", "success")

    return render_template("search_results.html", results=search_results)


@search_blueprint.route("/history")
def search_history():
    if "user_id" not in session:
        flash("You must be logged in to view your search history.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    try:
        # Use the `filter_by` method instead of `filter` to query by user_id
        history = db.session.query(SearchHistory).filter_by(user_id=user_id).all()
    except Exception as e:
        print(f"Error retrieving search history: {e}")
        flash("Could not fetch search history. Please try again later.", "danger")
        return render_template("history.html", history=[])
    
    return render_template("history.html", history=history)
