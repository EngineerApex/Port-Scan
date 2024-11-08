'''
from flask import Flask, request, Response
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

    
visited_urls = set()

# Function to spider URLs within the specified domain and based on a keyword
def spider_urls(url, keyword, domain):
    try:
        response = requests.get(url)
    except:
        print(f"Request failed: {url}")
        return []

    url_links = []  # This will store all the important links containing the keyword

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all("a")
        urls = [tag.get("href") for tag in a_tags if tag.get("href")]

        for link in urls:
            if link not in visited_urls:
                # Resolve relative URLs to absolute URLs
                url_join = urljoin(url, link)

                # Parse the URL to check if it matches the specified domain
                parsed_url = urlparse(url_join)
                if domain in parsed_url.netloc:  # Ensures link is within the domain
                    visited_urls.add(link)
                    if keyword in url_join:
                        url_links.append(url_join)
                        # Recursively call spider_urls for deeper crawling within the same domain
                        url_links.extend(spider_urls(url_join, keyword, domain))

    return url_links  # Return the list of important links

# Function to probe URLs for active or dead status
def spider_probe(url_list):
    good_urls = []
    bad_urls = []

    for url in url_list:
        try:
            response = requests.head(url, timeout=5)  # Using head request for faster response

            if response.status_code == 200:
                good_urls.append(url)
            else:
                bad_urls.append(url)

        except requests.exceptions.MissingSchema:
            bad_urls.append(url)
            continue

        except requests.exceptions.ConnectionError:
            bad_urls.append(url)
            continue

    # Convert the results into a formatted plain text string
    output = "[+] Active URLs:\n" + "\n".join(good_urls) + "\n\n[-] Dead URLs:\n" + "\n".join(bad_urls)
    return output

# Flask endpoint for spidering and probing
@app.route('/spider', methods=['POST'])
def spider_endpoint():
    data = request.get_json()
    url = data.get("url")
    keyword = data.get("keyword")

    if not url or not keyword:
        return Response("Both 'url' and 'keyword' are required", status=400)

    # Ensure the URL starts with http:// or https://
    if not url.startswith(("http://", "https://")):
        return Response("Invalid URL format. Please include http:// or https://", status=400)

    # Extract the domain from the URL to limit the crawling scope
    domain = urlparse(url).netloc

    # Set to keep track of visited URLs


    # Get all important links by crawling the website within the specified domain
    important_links = spider_urls(url, keyword, domain)

    # Check active and dead links from the list of important links
    output = spider_probe(important_links)

    # Return the output as plain text
    return Response(output, mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)
'''

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
    except:
        print(f"Request failed: {url}")
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

# Endpoint to initiate spidering and set up for streaming
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

    return Response("Spidering initiated.", status=200)

# SSE endpoint to stream results
@app.route('/spider-stream')
def spider_stream():
    return Response(stream_with_context(spider_probe(important_links)), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
