from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from zenrows import ZenRowsClient
import logging

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
    urls = [clean_url(link.get("href")) for link in links if link.get("href") and "url?q=" in link.get("href")]

    # Log URLs found
    logging.info(f"Found URLs: {urls}")

    # Iterate over the URLs and scrape data for each using ZenRows
    scraped_data = []
    for url in urls:
        detailed_data = scrape_with_zenrows(url)
        scraped_data.append({
            "url": url,
            "data": detailed_data
        })
    
    # Log scraped data
    logging.info(f"Scraped data: {scraped_data}")

    return jsonify({"urls": urls, "scraped_data": scraped_data})

def google_search(query):
    url = f"https://www.google.com/search?q={quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
        logging.error(f"Error fetching data: {response.status_code} for URL: {url}")
        return None

def clean_url(url):
    url = unquote(url)  # Decode URL
    if url.startswith('/url?q='):
        url = url.split('&')[0].replace('/url?q=', '')
    # Ensure URL is fully qualified
    if not urlparse(url).scheme:
        url = urljoin('https://www.google.com', url)
    return url

def scrape_with_zenrows(url):
    try:
        # Get the response from the ZenRows API
        response = client.get(url)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            logging.error(f"Resource not found (404): {url}")
            return {"error": "Resource not found (404)"}
        elif response.status_code == 400:
            logging.error(f"Bad request (400) for URL: {url}")
            return {"error": "Bad request (400). The URL may be malformed or missing parameters."}
        elif response.status_code == 403:
            logging.error(f"Access forbidden (403) for URL: {url}")
            return {"error": "Access forbidden (403). You might be blocked or your API key doesn't have access."}
        else:
            logging.error(f"Unexpected status code {response.status_code} for URL: {url}")
            return {"error": f"Unexpected status code {response.status_code}"}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": f"An error occurred: {e}"}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
