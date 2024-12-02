import requests

def perform_web_scraping_with_categories(query, category, API_KEY, CX, RESULT_COUNT=20):
    """
    Perform a web search using Google Custom Search API with category-based restrictions.

    Args:
        query (str): The search term entered by the user.
        category (str): The category for the search.
        API_KEY (str): API key for Google Custom Search API.
        CX (str): Custom Search Engine ID.
        RESULT_COUNT (int): Total number of results to fetch.

    Returns:
        list: A list of dictionaries containing the search results (title, link, snippet).
    """
    # Define category-specific site restrictions
    category_sites = {
        "social_media": "site:twitter.com OR site:facebook.com OR site:instagram.com",
        "ecommerce": "site:amazon.com OR site:ebay.com OR site:etsy.com",
        "blog": "site:medium.com OR site:blogger.com OR site:wordpress.com",
        "news": "site:cnn.com OR site:bbc.com OR site:nytimes.com",
        "technology": "site:techcrunch.com OR site:wired.com",
        "entertainment": "site:imdb.com OR site:rottentomatoes.com OR site:spotify.com"
    }

    search_sites = category_sites.get(category, "")

    search_results = []
    start = 1  # Pagination starts at 1

    while len(search_results) < RESULT_COUNT:
        try:
            # Construct the API request URL
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query} {search_sites}&start={start}&num=10"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            # Extract items from the API response
            items = data.get("items", [])
            for item in items:
                search_results.append({
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", "#"),
                    "snippet": item.get("snippet", "No description available.")
                })

            if not items:  # Break if no more results are available
                break
            start += 10  # Move to the next page

        except Exception as e:
            print(f"Error during web search: {e}")
            break

    return search_results[:RESULT_COUNT]
