import tldextract

def rank_search_results(results, query):
    """
    Rank search results based on relevance and domain priority.

    Args:
        results (list): List of dictionaries containing search results.
        query (str): The search query entered by the user.

    Returns:
        list: Sorted list of ranked search results.
    """
    def calculate_score(result):
        score = 0

        # Title match weight
        if query.lower() in result.get("title", "").lower():
            score += 50

        # Snippet match weight
        if query.lower() in result.get("snippet", "").lower():
            score += 30

        # Domain priority
        domain_priority = {
            ".edu": 20,
            ".gov": 20,
            ".org": 10
        }
        extracted = tldextract.extract(result.get("link", ""))
        domain_suffix = f".{extracted.suffix}"
        score += domain_priority.get(domain_suffix, 0)

        return score

    # Rank and sort results
    ranked_results = sorted(results, key=calculate_score, reverse=True)
    return ranked_results
