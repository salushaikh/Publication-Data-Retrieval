import requests

def fetch_google_scholar_data(api_key, query, max_results=10):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": api_key,
        "num": max_results
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error fetching data from Google Scholar:", response.json())
        return []

    data = response.json()
    scholar_data = []

    if "organic_results" not in data:
        print("No results found on Google Scholar.")
        return scholar_data

    for result in data["organic_results"]:
        publication_info = result.get("publication_info", {}).get("summary", "")
        author_name, publication_year = "", ""
        
        # Extract author name and year if available
        parts = publication_info.split(" - ")
        if len(parts) >= 2:
            author_name = parts[0].strip()
            year_match = next((part for part in parts[1:] if part.isdigit() and len(part) == 4), "")
            publication_year = year_match or ""

        resource_title = ""
        resource_format = ""
        resource_link = ""
        resources = result.get("resources", [])
        if resources:
            resource = resources[0]
            resource_title = resource.get("title", "")
            resource_format = resource.get("file_format", "")
            resource_link = resource.get("link", "")

        cited_by = result.get("inline_links", {}).get("cited_by", {})
        cited_by_total = cited_by.get("total", "")
        cited_by_link = cited_by.get("link", "")
        cited_by_id = cited_by.get("cites_id", "")

        versions = result.get("inline_links", {}).get("versions", {})
        versions_total = versions.get("total", "")
        versions_link = versions.get("link", "")
        versions_id = versions.get("cluster_id", "")
        
        # Replace any incorrectly encoded characters in the snippet
        cleaned_snippet = result.get("snippet", "").replace("â€¦", "...")

        # Alternatively, replace Unicode ellipsis if that's also causing issues:
        cleaned_snippet = cleaned_snippet.replace("…", "...")

        scholar_entry = {
            "Source": "GS",
            "Title": result.get("title", ""),
            "Snippet": cleaned_snippet,
            "Author Name": author_name,
            "Publication Year": publication_year,
            "Resource Title": resource_title,
            "Resource Link": resource_link,
            "Cited By Link": cited_by_link,
            "Versions Link": versions_link
        }
        
        scholar_data.append(scholar_entry)

    return scholar_data
