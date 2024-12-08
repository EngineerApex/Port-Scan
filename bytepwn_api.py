from flask import Flask, request, Response, jsonify, stream_with_context
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

app = Flask(__name__)
CORS(app)

#######################################
# Directory Bruteforce (First Code)
#######################################
wordlist_dir = [
    "admin", "login", "user", "dashboard", "uploads", "assets", "css", "js", "images", "backup",
    "api", "config", "downloads", "docs", "includes", "lib", "public", "private", "test", "temp",
    "data", "scripts", "src", "themes", "vendor", "app", "cgi-bin", "server-status", "portal", "services",
    "files", "about", "contact", "faq", "help", "news", "support", "blog", "wp-admin", "wp-content", "uploads",
    "media", "sitemap", "robots.txt", "api-docs", "status", "database", "vulnerabilities", "index"
]
scanned_results_dir = []  # Results for directory bruteforce

def stream_brute_force_directories(url):
    global scanned_results_dir
    scanned_results_dir = []

    if not url.startswith("http"):
        url = "http://" + url

    for word in wordlist_dir:
        full_url = f"{url}/{word}"
        try:
            response = requests.get(full_url)
            if response.status_code in [200, 403]:
                result = f"[+] Found: {full_url} (Status: {response.status_code})"
                scanned_results_dir.append(result)
        except requests.exceptions.RequestException as e:
            scanned_results_dir.append(f"[!] Error accessing {full_url}: {e}")
        time.sleep(0.2)

@app.route('/bruteforce', methods=['POST'])
def start_scan_dir():
    data = request.json
    target_url = data.get('url', '')

    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # Perform brute force immediately (no separate thread)
    stream_brute_force_directories(target_url)
    return jsonify({"message": "Scan completed. Use /bruteforce-stream to get results."}), 200

@app.route('/bruteforce-stream', methods=['GET'])
def stream_results_dir():
    def event_stream():
        for result in scanned_results_dir:
            yield f"data:{result}\n\n"
            time.sleep(0.1)
    return Response(event_stream(), content_type='text/event-stream')

#######################################
# Subdomain Bruteforce (Second Code)
#######################################
subdomains = [
    "www", "mail", "ftp", "webmail", "smtp", "admin", "blog", "store", "test", "api",
    "dev", "support", "cpanel", "forum", "help", "vpn", "news", "shop", "demo", "portal",
    "beta", "secure", "mobile", "staging", "cloud", "status", "docs", "www2", "intranet", "public",
    "ns1", "ns2", "dns", "files", "backup", "mx", "images", "cdn", "crm", "office",
    "accounts", "app", "billing", "download", "chat", "my", "static", "video", "search", "login"
]
scanned_results_subd = []  # Results for subdomain bruteforce

def brute_force_subdomains(domain):
    global scanned_results_subd
    scanned_results_subd = []

    for subdomain in subdomains:
        full_url = f"http://{subdomain}.{domain}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200 or response.status_code == 403:
                result = f"[+] Found: {full_url} (Status: {response.status_code})"
                scanned_results_subd.append(result)
        except requests.exceptions.RequestException:
            pass

@app.route('/subd', methods=['POST'])
def start_scan_subd():
    data = request.json
    target_domain = data.get('url', '')

    if not target_domain:
        return jsonify({"error": "Domain is required"}), 400

    brute_force_subdomains(target_domain)
    return jsonify({"message": "Subdomain scan completed. Use /subd-stream to get results."})

@app.route('/subd-stream', methods=['GET'])
def stream_results_subd():
    def event_stream():
        for result in scanned_results_subd:
            yield f"data:{result}\n\n"
    return Response(event_stream(), content_type='text/event-stream')

#######################################
# Spider and Probe (Third Code)
#######################################
'''
visited_urls = set()
important_links = []  # For spider
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
        time.sleep(0.5)

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
    important_links = spider_urls(url, keyword, domain)

    if not important_links:
        return Response("No links found for the given keyword.", status=200)

    return Response(stream_with_context(spider_probe(important_links)), mimetype='text/plain')

##############################################
visited_urls = set()

def spider_urls(url, keyword, domain, max_links=50):
    # Non-recursive approach: just scan this page and stop.
    # Or if you want multi-level, implement a queue-based approach with a limit.
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed: {url} - {e}")
        return []

    found_links = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all("a")
        urls = [tag.get("href") for tag in a_tags if tag.get("href")]

        # Limit how many links we process to prevent timeouts
        for link in urls[:max_links]:
            if link not in visited_urls:
                url_join = urljoin(url, link)
                parsed_url = urlparse(url_join)
                if domain in parsed_url.netloc:
                    visited_urls.add(link)
                    if keyword in url_join:
                        # Just store links found in one level
                        # If you want multi-level scanning, you'd add them to a queue and process iteratively.
                        found_links.append(url_join)
    return found_links

def spider_probe(url_list):
    # Remove sleeps and yield responses as quickly as possible
    for url in url_list:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                yield f"data: [+] Active: {url}\n\n"
            else:
                yield f"data: [-] Dead: {url}\n\n"
        except requests.exceptions.RequestException:
            yield f"data: [-] Dead: {url}\n\n"

@app.route('/spider', methods=['POST'])
def spider_endpoint():
    data = request.get_json()
    url = data.get("url")
    keyword = data.get("keyword")

    if not url or not keyword:
        return Response("Both 'url' and 'keyword' are required", status=400)

    if not url.startswith(("http://", "https://")):
        return Response("Invalid URL format. Please include http:// or https://", status=400)

    global visited_urls
    visited_urls = set()
    domain = urlparse(url).netloc
    # Limit to a small number of links
    important_links = spider_urls(url, keyword, domain, max_links=20)

    if not important_links:
        return Response("No links found for the given keyword.", status=200)

    return Response(stream_with_context(spider_probe(important_links)), mimetype='text/plain')
'''
@app.route('/spider', methods=['POST'])
def spider_endpoint():
    data = request.get_json()
    url = data.get("url")
    keyword = data.get("keyword")

    if not url or not keyword:
        return Response("Both 'url' and 'keyword' are required", status=400)

    if not url.startswith(("http://", "https://")):
        return Response("Invalid URL format. Please include http:// or https://", status=400)

    try:
        # Fetch the initial page
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all("a")
        # Extract all links containing the keyword
        links = []
        for tag in a_tags:
            href = tag.get("href")
            if href and keyword in href:
                full_url = urljoin(url, href)
                links.append(full_url)

        if not links:
            return Response("No links found for the given keyword.", status=200)

        # Probe each link to see if it's active or dead
        results = []
        for link in links:
            try:
                head_resp = requests.head(link, timeout=5)
                if head_resp.status_code == 200:
                    results.append(f"[+] Active: {link}")
                else:
                    results.append(f"[-] Dead: {link}")
            except requests.exceptions.RequestException:
                results.append(f"[-] Dead: {link}")

        # Return all results as plain text
        return Response("\n".join(results), mimetype='text/plain')

    except requests.RequestException as e:
        return Response(f"Failed to process the request: {e}", status=500)


#######################################
# Webscrape (Fourth Code)
#######################################
@app.route('/webscrape', methods=['POST'])
def webscrape():
    data = request.get_json()
    url = data.get("url")
    tag = data.get("keyword")

    if not url or not tag:
        return jsonify({"error": "Both URL and tag are required"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(tag)

        links = []
        for element in elements:
            href = element.get("href")
            if href:
                full_url = urljoin(url, href)
                links.append(full_url)
            else:
                links.append(str(element))

        return Response("\n".join(links), mimetype='text/plain')

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to scrape the website: {e}"}), 500

#######################################
# Main Entry
#######################################
if __name__ == "__main__":
    app.run(debug=True)
