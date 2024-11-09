import streamlit as st
import csv
import os
import pandas as pd
import json
from google_books_module import fetch_google_books_data
from google_scholar_module import fetch_google_scholar_data
from network_graph_module import generate_network_graph

# Load API keys from a config file
def load_api_keys():
    if os.path.exists("api_keys.json"):
        with open("api_keys.json", "r") as file:
            return json.load(file)
    return {"google_books": "", "google_scholar": ""}

# Save API keys to a config file
def save_api_keys(api_keys):
    with open("api_keys.json", "w") as file:
        json.dump(api_keys, file)

# Initialize API keys in session state if not already set
if "api_keys" not in st.session_state:
    st.session_state.api_keys = load_api_keys()

# Sidebar: Settings for API Keys with a dropdown expander
with st.sidebar.expander("API Keys"):
    google_books_key = st.text_input("Google Books API Key", type="password", value=st.session_state.api_keys.get("google_books"))
    google_scholar_key = st.text_input("Google Scholar API Key", type="password", value=st.session_state.api_keys.get("google_scholar"))

    # Save the API keys if they were updated
    if google_books_key != st.session_state.api_keys["google_books"] or google_scholar_key != st.session_state.api_keys["google_scholar"]:
        st.session_state.api_keys["google_books"] = google_books_key
        st.session_state.api_keys["google_scholar"] = google_scholar_key
        save_api_keys(st.session_state.api_keys)

# Function to retrieve data and return as list of dictionaries
def retrieve_combined_data(query, max_results, api_keys):
    google_books_data = fetch_google_books_data(api_keys["google_books"], query, max_results)
    google_scholar_data = fetch_google_scholar_data(api_keys["google_scholar"], query, max_results)

    # Combine data from both sources
    combined_data = google_books_data + google_scholar_data
    return combined_data

# Function to update or create CSV file with new data
def update_csv_file(file_name, combined_data):
    # Fieldnames for the CSV, ensure these cover both Google Books and Scholar data
    fieldnames = [
        "Title", "Snippet", "Author Name", "Publication Year", "Publisher", "Publication Date",
        "Description", "ISBN Identifiers", "Page Count", "Categories", "Content Version",
        "Image Links", "Language", "Resource Title", "Resource Link",
        "Cited By Link", "Versions Link"
    ]
    
    # Check if the file exists and create it if not, with headers
    file_exists = os.path.isfile(file_name)
    
    # Initialize an empty set for existing titles if file is missing or without headers
    existing_titles = set()
    
    # Try to read the existing titles if file exists and not empty
    if file_exists and os.path.getsize(file_name) > 0:
        with open(file_name, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            try:
                # Gather existing titles to avoid duplication
                existing_titles = {row["Title"] for row in reader}
            except KeyError:
                print("Warning: 'Title' column is missing in CSV file. Rewriting headers.")
    
    # Open the file in append mode and write new data
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write headers if the file is new or was missing headers
        if not file_exists or os.path.getsize(file_name) == 0:
            writer.writeheader()
        
        # Write only new data rows to avoid duplicates
        for data in combined_data:
            if data.get("Title") not in existing_titles:
                writer.writerow(data)

# Main query and file name input
st.header("Data Retrieval for Books and Scholar Information")
st.write("Enter your query and retrieval options below:")

query = st.text_input("Search Query", "")
max_results = st.number_input("Max Results From Each Source (enter '0' for all data)", min_value=0, step=1)

# Dropdown for selecting an existing CSV file or input for a new filename
existing_files = [f for f in os.listdir() if f.endswith('.csv')]
file_name = st.selectbox("Select existing CSV file or enter new name", options=["<New File>"] + existing_files)
if file_name == "<New File>":
    file_name = st.text_input("New CSV File Name", "combined_data.csv")

# Button to start data retrieval
if st.button("Retrieve Data"):
    if not query:
        st.error("Please enter a search query.")
    elif not st.session_state.api_keys["google_books"] or not st.session_state.api_keys["google_scholar"]:
        st.error("Please provide API keys for both Google Books and Google Scholar.")
    else:
        # Retrieve data from both sources
        combined_data = retrieve_combined_data(query, max_results, st.session_state.api_keys)
        
        # Update CSV file with combined data
        update_csv_file(file_name, combined_data)
        st.success(f"Data retrieval successful! Data saved to `{file_name}`")

# Sidebar Header for Download Section
st.sidebar.header("Download Data")

# Fetch all CSV files in the current directory
existing_files = [f for f in os.listdir() if f.endswith('.csv')]

# Display a selectbox with existing CSV files for user to choose from
f_name = st.sidebar.selectbox("Select CSV file", options=existing_files)

# Check if the selected file exists and display a download button
if f_name and os.path.isfile(f_name):
    with open(f_name, "rb") as file:
        st.sidebar.download_button(
            label="Download CSV File",
            data=file.read(),
            file_name=f_name,
            mime="text/csv"
         )

st.sidebar.write("Double-click on the CSV file name in your file explorer to open and edit directly.")
