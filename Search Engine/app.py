from flask import Flask, render_template, request, send_file
from storage import DBStorage
from datetime import datetime
import requests
import signal
import csv
import sys

# Initialize the database and Flask app
db = DBStorage()
app = Flask(__name__)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nGracefully shutting down the server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Google Custom Search API key and CX
API_KEY = "AIzaSyBiXTEPooZiuotBUXaipIoMZCCiOFOiUc4"
CX = "b213191287aba4aef"  # Your Custom Search Engine ID
RESULT_COUNT = 20  # Total results to fetch (across multiple pages)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()
    search_results = []

    # Validate input
    if not query or not category:
        return render_template('search.html', query=query, category=category, results=[],
                               error="Please provide both a query and a category.")

    # Save the query to the CSV file
    csv_file_path = 'search_history.csv'
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([query, category, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    # Load data from the CSV file into the database
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:  # Ensure row has at least query and category
                    query, category = row[0], row[1]
                    timestamp = row[2] if len(row) > 2 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    db.save_search_query(query, category)
    except Exception as e:
        print(f"Error loading data from CSV to DB: {e}")

    # Fetch search results from Google Custom Search API
    try:
        # Define category-specific site restrictions
        category_sites = {
            "social_media": "site:twitter.com OR site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:pinterest.com OR site:snapchat.com OR site:tiktok.com",
            "ecommerce": "site:amazon.com OR site:ebay.com OR site:etsy.com OR site:walmart.com OR site:bestbuy.com",
            "blog": "site:medium.com OR site:blogger.com OR site:wordpress.com OR site:substack.com OR site:hashnode.com",
            "news": "site:cnn.com OR site:bbc.com OR site:nytimes.com OR site:theguardian.com OR site:forbes.com OR site:reuters.com",
            "technology": "site:techcrunch.com OR site:wired.com OR site:thenextweb.com OR site:arstechnica.com OR site:venturebeat.com",
            "entertainment": "site:imdb.com OR site:rottentomatoes.com OR site:netflix.com OR site:hulu.com OR site:disneyplus.com OR site:spotify.com"
        }
        search_sites = category_sites.get(category, "")
        
        start = 1  # Start with the first page
        while len(search_results) < RESULT_COUNT:
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query} {search_sites}&start={start}&num=10"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for HTTP issues
            data = response.json()
            items = data.get('items', [])
            search_results.extend(items)
            if not items:  # No more results
                break
            start += 10  # Move to the next page
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")
        return render_template('search.html', query=query, category=category, results=[],
                               error="Error fetching search results. Please try again later.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return render_template('search.html', query=query, category=category, results=[],
                               error="An unexpected error occurred. Please try again later.")

    # Limit the results to the specified count
    search_results = search_results[:RESULT_COUNT]

    return render_template('search.html', query=query, category=category, results=search_results)
@app.route('/history')
def history():
    try:
        # Retrieve search history from the database
        search_history = db.get_search_history()
        
        # Ensure search_history is converted to a list of dictionaries
        history_list = [
            {"query": record.query, "category": record.category, "timestamp": record.timestamp}
            for record in search_history
        ]

        return render_template('history.html', history=history_list)
    except Exception as e:
        print(f"Error fetching history: {e}")
        return render_template('history.html', history=[], error="Could not fetch search history.")


@app.route('/export_history')
def export_history():
    # Export search history to a CSV file
    try:
        search_history = db.get_search_history()
        csv_file = './search_history.csv'
        search_history.to_csv(csv_file, index=False)
        return send_file(csv_file, as_attachment=True, download_name='search_history.csv')
    except Exception as e:
        print(f"Error exporting search history: {e}")
        return f"Error exporting search history: {e}"

@app.route('/favorites', methods=['GET'])
def favorites():
    # Retrieve favorite search results from the database
    try:
        favorite_results = db.get_favorites()
        return render_template('favorites.html', favorites=favorite_results.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return render_template('favorites.html', favorites=[], error="Could not fetch favorites.")

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    # Add a search result to favorites
    data = request.json  # Assuming data is sent as JSON from the frontend
    try:
        db.add_to_favorites(data['query'], data['link'], data['title'], data['snippet'])
        return {'status': 'success', 'message': 'Added to favorites successfully'}, 200
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
    signal.signal(signal.SIGINT, signal_handler)
