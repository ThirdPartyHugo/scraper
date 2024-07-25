from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def clean_url(url):
    url = url.split('&')[0].replace('/url?q=', '')
    return url

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    soup = google_search(query)
    links = soup.find_all("a")
    urls = [clean_url(link.get("href")) for link in links if "url?q=" in link.get("href")]
    
    return urls

if __name__ == '__main__':
    app.run(debug=True)
