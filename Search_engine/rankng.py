import tldextract
from utils import compute_tfidf, cosine_similarity

def rank_search_results(results, query, documents):
    """
    Rank search results based on TF-IDF scores and domain priority.

    Args:
        results (list): List of dictionaries containing search results.
        query (str): The search query entered by the user.
        documents (list): Text content of all search results for TF-IDF computation.

    Returns:
        list: Sorted list of ranked search results.
    """

    # Compute TF-IDF for query and documents
    query_tfidf = compute_tfidf(query, documents)
    doc_tfidf = [compute_tfidf(doc, documents) for doc in documents]

    def calculate_score(result, doc_index):
        # Base score from TF-IDF Cosine Similarity
        score = cosine_similarity(query_tfidf, doc_tfidf[doc_index])

        # Domain priority boost
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
    ranked_results = sorted(
        enumerate(results),
        key=lambda x: calculate_score(x[1], x[0]),
        reverse=True
    )
    return [results[i[0]] for i in ranked_results]
