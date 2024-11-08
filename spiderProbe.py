from flask import Flask, request, Response, stream_with_context
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

visited_urls = set()
important_links = []  # Store the links to be streamed

# Function to spider URLs within the specified domain and based on a keyword
def spider_urls(url, keyword, domain):
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Request failed: {url} - {e}")
        return []

    url_links = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all("a")
        urls = [tag.get("href") for tag in a_tags if tag.get("href")]

        for link in urls:
            if link not in visited_urls:
                url_join = urljoin(url, link)
                parsed_url = urlparse(url_join)
                if domain in parsed_url.netloc:
                    visited_urls.add(link)
                    if keyword in url_join:
                        url_links.append(url_join)
                        url_links.extend(spider_urls(url_join, keyword, domain))

    return url_links

# Function to probe URLs for active or dead status and yield results for streaming
def spider_probe(url_list):
    for url in url_list:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                yield f"data: [+] Active: {url}\n\n"
            else:
                yield f"data: [-] Dead: {url}\n\n"
        except requests.exceptions.RequestException:
            yield f"data: [-] Dead: {url}\n\n"
        time.sleep(0.5)  # Optional delay to simulate real-time streaming

# Combined endpoint to initiate spidering and stream results
@app.route('/spider', methods=['POST'])
def spider_endpoint():
    data = request.get_json()
    url = data.get("url")
    keyword = data.get("keyword")

    if not url or not keyword:
        return Response("Both 'url' and 'keyword' are required", status=400)

    if not url.startswith(("http://", "https://")):
        return Response("Invalid URL format. Please include http:// or https://", status=400)

    global visited_urls, important_links
    visited_urls = set()
    domain = urlparse(url).netloc
    important_links = spider_urls(url, keyword, domain)  # Store links for streaming

    if not important_links:
        return Response("No links found for the given keyword.", status=200)

    # Stream the probing results
    return Response(stream_with_context(spider_probe(important_links)), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)
