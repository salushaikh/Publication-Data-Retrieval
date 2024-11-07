import requests
import csv
import os
import re

def fetch_google_scholar_data(api_key, query, file_name="scholar_data.csv"):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print("Error fetching data:", response.json())
        return

    data = response.json()
    
    if "organic_results" not in data:
        print("No results found.")
        return

    # Check if file exists and load existing titles to prevent duplicates
    existing_titles = set()
    if os.path.isfile(file_name):
        with open(file_name, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_titles = {row["Title"] for row in reader}

    rows_to_write = []
    for i in range(4): #data["organic_results"]:
        item = data["organic_results"][i]
        title = item.get("title", "")
        
        # Skip if title already exists in CSV
        if title in existing_titles:
            print(f'The article "{title}" already exists in {file_name}. Skipping entry.')
            continue

        # Extract required fields
        snippet = item.get("snippet", "")
        publication_info = item.get("publication_info", {}).get("summary", "").split(" - ")
        author_name = publication_info[0] if len(publication_info) > 0 else ""
        #publication_year = publication_info[1] if len(publication_info) > 1 else ""

        # Use regex to extract a valid 4-digit year
        publication_year = ""
        if len(publication_info) > 1:
            year_match = re.search(r"\b(19|20)\d{2}\b", publication_info[1])
            if year_match:
                publication_year = year_match.group(0)

        resources = item.get("resources", [])
        resource_title = resources[0].get("title", "") if resources else ""
        resource_file_format = resources[0].get("file_format", "") if resources else ""
        resource_link = resources[0].get("link", "") if resources else ""
        
        cited_by = item.get("inline_links", {}).get("cited_by", {})
        cited_by_total = cited_by.get("total", "")
        cited_by_link = cited_by.get("link", "")
        cited_by_id = cited_by.get("cites_id", "")
        
        versions = item.get("inline_links", {}).get("versions", {})
        versions_total = versions.get("total", "")
        versions_link = versions.get("link", "")
        versions_cluster_id = versions.get("cluster_id", "")

        # Prepare row data for CSV
        row = {
            "Title": title,
            "Snippet": snippet,
            "Author Name": author_name,
            "Publication Year": publication_year,
            "Resource Title": resource_title,
            "Resource File Format": resource_file_format,
            "Resource Link": resource_link,
            "Cited By Total": cited_by_total,
            "Cited By Link": cited_by_link,
            "Cited By ID": cited_by_id,
            "Versions Total": versions_total,
            "Versions Link": versions_link,
            "Versions Cluster ID": versions_cluster_id
        }
        rows_to_write.append(row)

    # Append rows to CSV
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows_to_write)

    print(f"Data retrieval successful! Updated {file_name}")

# Replace 'YOUR_API_KEY' with your actual SerpAPI key and 'your_query' with the search query
api_key = "your_api_key"
query = "biology"
file_name = "scholar_data.csv"
fetch_google_scholar_data(api_key, query, file_name)
