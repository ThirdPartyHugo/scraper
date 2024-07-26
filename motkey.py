from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from zenrows import ZenRowsClient

app = Flask(__name__)

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Set a timeout for the request
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during Google search: {e}")
        return None

def clean_url(url):
    url = url.split('&')[0].replace('/url?q=', '')
    return url

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    soup = google_search(query)
    if not soup:
        return jsonify({"error": "Failed to fetch data from Google"}), 500
    
    links = soup.find_all("a")
    urls = [clean_url(link.get("href")) for link in links if "url?q=" in link.get("href")]
    
    scraped_data = []
    for index, url in enumerate(urls):
        if index == 1:
            data = scrapeData(url)
        else:
            data = None  # Or some default value or handling

        scraped_data.append({
            "url": url,
            "data": data
        })

    
    return jsonify(scraped_data)

def scrapeData(url):
    try:
        client = ZenRowsClient("68904253c46be2ad491229afc13e3785baf61f0e")
        response = client.get(url, timeout=100)  # Set a timeout for the request
        if response.status_code == 200:
            data = response.text
        else:
            data = f"Error: Received status code {response.status_code}"
    except Exception as e:
        data = f"An error occurred: {e}"
    return data

if __name__ == '__main__':
    app.run(debug=True)
