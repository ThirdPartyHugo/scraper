from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from zenrows import ZenRowsClient
from fpdf import FPDF

app = Flask(__name__)

# Initialize the ZenRows client with your API key
ZENROWS_API_KEY = "68904253c46be2ad491229afc13e3785baf61f0e"
client = ZenRowsClient(ZENROWS_API_KEY)

@app.route('/')
def home():
    return "Welcome to the Search API. Use /search?query=<your_query> to search."

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
    
    # For demonstration, let's scrape one of the URLs using ZenRows
    # This can be adjusted based on your actual use case
    if urls:
        detailed_data = scrape_with_zenrows(urls[0])
        return jsonify({"urls": urls, "detailed_data": detailed_data})
    return jsonify(urls)

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    return None

def clean_url(url):
    url = url.split('&')[0].replace('/url?q=', '')
    return url

def scrape_with_zenrows(url):
    try:
        # Get the response from the ZenRows API
        response = client.get(url)
        if response.status_code == 200:
            return {"data": response.text}  # Assuming the response is text-based
        else:
            return {"error": f"Received status code {response.status_code}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

if __name__ == '__main__':
    app.run(debug=True)
