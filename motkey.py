from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from zenrows import ZenRowsClient

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
    
    scraped_data = []
    for url in urls:
        data = scrapeData(url)
        scraped_data.append({
            "url": url,
            "data": data
        })
    return scraped_data

def scrapeData(url):
    try:
        # Get the response from the API
        response = client.get(url)
        if response.status_code == 200:
            data = response.text  # Assuming the response is text-based
        else:
            data = f"Error: Received status code {response.status_code}"
    except Exception as e:
        data = f"An error occurred: {e}"
    

if __name__ == '__main__':
    app.run(debug=True)
