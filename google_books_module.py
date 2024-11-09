import requests

def fetch_google_books_data(api_key, query, max_results=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        "maxResults": max_results
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print("Error fetching data from Google Books:", response.json())
        return []
    
    data = response.json()
    books_data = []
    
    if "items" not in data:
        print("No results found on Google Books.")
        return books_data

    for book in data["items"]:
        volume_info = book.get("volumeInfo", {})
        
        industry_identifiers = ", ".join(
            f"{id_type['type']}: {id_type['identifier']}" 
            for id_type in volume_info.get("industryIdentifiers", [])
        )

        book_data = {
            "Source": "GB",
            "Title": volume_info.get("title", ""),
            "Snippet": volume_info.get("description", ""), 
            "Author Name": ", ".join(volume_info.get("authors", [])),
            "Publication Year": volume_info.get("publishedDate", "")[:4],
            "Publisher": volume_info.get("publisher", ""),
            "Publication Date": volume_info.get("publishedDate", ""),
            "Description": volume_info.get("description", ""),
            "ISBN Identifiers": industry_identifiers,
            "Page Count": volume_info.get("pageCount", ""),
            "Categories": ", ".join(volume_info.get("categories", [])),
            "Content Version": volume_info.get("contentVersion", ""),
            "Image Links": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            "Language": volume_info.get("language", "")
        }
        
        books_data.append(book_data)

    return books_data
