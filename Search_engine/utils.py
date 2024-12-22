import re
import math
from collections import Counter
import requests

# Preprocessing: Tokenization
def tokenize(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z0-9\\s]', '', text)  # Remove special characters
    return text.split()

# Remove Stopwords
def remove_stopwords(tokens):
    stopwords = set(['the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'on', 'with', 'at', 'by'])
    return [token for token in tokens if token not in stopwords]

# Compute Term Frequency (TF)
def compute_tf(doc):
    tokens = tokenize(doc)
    tokens = remove_stopwords(tokens)
    term_count = Counter(tokens)
    total_terms = len(tokens)
    return {term: count / total_terms for term, count in term_count.items()}

# Compute Inverse Document Frequency (IDF)
def compute_idf(docs):
    num_docs = len(docs)
    idf = {}
    all_tokens = set(token for doc in docs for token in tokenize(doc))

    for token in all_tokens:
        count = sum(1 for doc in docs if token in tokenize(doc))
        idf[token] = math.log(num_docs / (1 + count)) + 1

    return idf

# Compute TF-IDF Scores
def compute_tfidf(doc, docs):
    tf = compute_tf(doc)
    idf = compute_idf(docs)
    return {term: tf[term] * idf.get(term, 0) for term in tf}

# Cosine Similarity
def cosine_similarity(vec1, vec2):
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in set(vec1) | set(vec2))
    magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0

# Perform Web Scraping with Google Custom Search API
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

    # Allow dynamic categories by using the query directly if the category doesn't exist
    search_sites = category_sites.get(category, "")

    # Prepare search results
    search_results = []
    seen_links = set()  # To avoid duplicate results
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
                link = item.get("link", "#")
                if link not in seen_links:  # Avoid duplicate links
                    search_results.append({
                        "title": item.get("title", "No Title"),
                        "link": link,
                        "snippet": item.get("snippet", "No description available.")
                    })
                    seen_links.add(link)  # Add link to the set

            # Stop fetching if no more results are available
            if not items:
                break
            start += 10  # Move to the next page

        except requests.exceptions.RequestException as e:
            print(f"Network error during web search: {e}")
            break
        except Exception as e:
            print(f"Error during web search: {e}")
            break

    # Return the top 'RESULT_COUNT' results
    return search_results[:RESULT_COUNT]
