from ddgs import DDGS

def fetch_news(query, max_articles=5):
    try:
        results = []
        ddgs = DDGS()
        search_results = ddgs.news(query, region="in-en", safesearch="off", max_results=max_articles)
        for r in search_results:
            title = r.get("title", "")
            body = r.get("body", "")
            source = r.get("source", "")
            results.append(f"{title} ({source}): {body}")
        return results
    except Exception as e:
        print(f"News fetch error: {e}")
        return []

def fetch_web(query, max_results=3):
    try:
        results = []
        ddgs = DDGS()
        search_results = ddgs.text(query, region="in-en", safesearch="off", max_results=max_results)
        for r in search_results:
            title = r.get("title", "")
            body = r.get("body", "")
            results.append(f"{title}: {body}")
        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []