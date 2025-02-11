from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from database import db
from models import SearchHistory, Favorite
from utils import perform_web_scraping_with_categories
from rankng import rank_search_results
from json import dumps

search_blueprint = Blueprint("search", __name__)

API_KEY = "Your_Google_API_Key_here"
CX = "b213191287aba4aef"

@search_blueprint.route("/", methods=["GET", "POST"])
def search_page():
    if "user_id" not in session:
        flash("You must be logged in to access the search page.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        # Show the search form (home page)
        return render_template("home.html")

    # Handle the search query and display results
    query = request.form.get("query")
    category = request.form.get("category")

    if not query or not category:
        flash("Both search query and category are required.", "danger")
        return redirect(url_for("search.search_page"))

    # Perform the search and rank the results
    search_results = perform_web_scraping_with_categories(query, category, API_KEY, CX)
    # Prepare documents for TF-IDF calculation
    documents = [result['snippet'] for result in search_results]

    # Rank results using improved algorithm
    ranked_results = rank_search_results(search_results, query, documents)

    # Save ranked search results to search history
    user_id = session["user_id"]
    history_entry = SearchHistory(user_id=user_id, query=query, results=ranked_results)
    db.session.add(history_entry)
    db.session.commit()

    flash("Search completed successfully!", "success")
    return render_template("search.html", results=ranked_results, query=query, category=category)


@search_blueprint.route("/history")
def search_history():
    if "user_id" not in session:
        flash("You must be logged in to view your search history.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    try:
        # Retrieve search history for the logged-in user
        history = db.session.query(SearchHistory).filter_by(user_id=user_id).all()
    except Exception as e:
        print(f"Error retrieving search history: {e}")
        flash("Could not fetch search history. Please try again later.", "danger")
        return render_template("history.html", history=[])
    
    return render_template("history.html", history=history)


@search_blueprint.route("/add_favorite", methods=["POST"])
def add_favorite():
    if "user_id" not in session:
        return {"message": "You must be logged in to add favorites."}, 403

    data = request.json
    query = data.get("query")
    link = data.get("link")
    title = data.get("title")
    snippet = data.get("snippet")

    if not all([query, link, title, snippet]):
        return {"message": "Missing data. Please provide all required fields."}, 400

    # Save the favorite to the database
    try:
        favorite = Favorite(
            user_id=session["user_id"],
            query=query,
            link=link,
            title=title,
            snippet=snippet,
        )
        db.session.add(favorite)
        db.session.commit()
        return {"message": "Added to favorites successfully!"}, 200
    except Exception as e:
        print(f"Error saving favorite: {e}")
        return {"message": "An error occurred while saving the favorite."}, 500


@search_blueprint.route("/favorites", methods=["GET"])
def view_favorites():
    if "user_id" not in session:
        flash("You must be logged in to view your favorites.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    # Fetch favorites from the database
    favorites = db.session.query(Favorite).filter_by(user_id=user_id).all()

    return render_template("favorites.html", favorites=favorites)


@search_blueprint.route("/remove_favorite/<int:favorite_id>", methods=["POST"])
def remove_favorite(favorite_id):
    if "user_id" not in session:
        return {"message": "You must be logged in to remove favorites."}, 403

    try:
        favorite = db.session.query(Favorite).filter_by(id=favorite_id, user_id=session["user_id"]).first()
        if not favorite:
            return {"message": "Favorite not found or access denied."}, 404

        db.session.delete(favorite)
        db.session.commit()

        # Fetch the updated favorites list
        updated_favorites = db.session.query(Favorite).filter_by(user_id=session["user_id"]).all()
        favorites_list = [
            {"id": fav.id, "title": fav.title, "link": fav.link, "snippet": fav.snippet, "query": fav.query}
            for fav in updated_favorites
        ]
        return {"message": "Removed from favorites successfully!", "favorites": favorites_list}, 200
    except Exception as e:
        print(f"Error removing favorite: {e}")
        return {"message": "An error occurred while removing the favorite."}, 500
