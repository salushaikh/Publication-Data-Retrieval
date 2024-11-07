import requests
import csv
import os

def save_book_data_to_csv(api_key, query, file_name="BookData.csv"):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        "maxResults": 2  # Change maxResults to 8 to retrieve up to 8 books
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error fetching data:", response.json())
        return

    data = response.json()

    if "items" not in data:
        print("No results found.")
        return

    # Loop only over the available items to avoid IndexError
    for book in data["items"]:
        volume_info = book.get("volumeInfo", {})

        # Check if the file already exists and load existing titles
        existing_titles = set()
        if os.path.isfile(file_name):
            with open(file_name, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                existing_titles = {row["Title"] for row in reader}

        # Skip if title already exists
        if volume_info.get("title") in existing_titles:
            print(f'The book "{volume_info.get("title")}" already exists in {file_name}. Skipping entry.')
            continue

        # Extract relevant fields
        industry_identifiers = ", ".join(
            f"{id['type']}: {id['identifier']}" for id in volume_info.get("industryIdentifiers", [])
        )
        data_dict = {
            "Title": volume_info.get("title"),
            "Authors": ", ".join(volume_info.get("authors", [])),
            "Publisher": volume_info.get("publisher"),
            "Publication Date": volume_info.get("publishedDate"),
            "Description": volume_info.get("description", ""),
            "ISBN Identifiers": industry_identifiers,
            "Page Count": volume_info.get("pageCount"),
            "Main Category": volume_info.get("mainCategory"),
            "Categories": ", ".join(volume_info.get("categories", [])),
            "Average Rating": volume_info.get("averageRating"),
            "Ratings Count": volume_info.get("ratingsCount"),
            "Content Version": volume_info.get("contentVersion"),
            "Image Links": volume_info.get("imageLinks", {}).get("thumbnail"),
            "Language": volume_info.get("language")
        }

        # Append data to CSV
        file_exists = os.path.isfile(file_name)
        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data_dict.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data_dict)

    print(f"Data retrieval successful! Updated {file_name}")

# Replace 'YOUR_API_KEY' with your actual Google Books API key and 'your_query' with the book query you want to search for
api_key = "your_api_key"
query = "Biology"
file_name = "booksdata.csv"  # Use your desired file name here
save_book_data_to_csv(api_key, query, file_name)
