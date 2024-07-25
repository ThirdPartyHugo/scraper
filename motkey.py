from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from zenrows import ZenRowsClient

app = Flask(__name__)

# Replace with your actual ZenRows API key
ZENROWS_API_KEY = '68904253c46be2ad491229afc13e3785baf61f0e'
client = ZenRowsClient(ZENROWS_API_KEY)

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    # Using ZenRows to fetch the page content
    response = client.get(url, params={"autoparse": "true"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
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
    if soup:
        links = soup.find_all("a")
        urls = [clean_url(link.get("href")) for link in links if "url?q=" in link.get("href")]
        return jsonify(urls)
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

if __name__ == '__main__':
    app.run(debug=True)
