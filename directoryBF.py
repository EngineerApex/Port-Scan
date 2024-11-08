from flask import Flask, request, Response, jsonify 
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

wordlist = [
    "admin", "login", "user", "dashboard", "uploads", "assets", "css", "js", "images", "backup",
    "api", "config", "downloads", "docs", "includes", "lib", "public", "private", "test", "temp",
    "data", "scripts", "src", "themes", "vendor", "app", "cgi-bin", "server-status", "portal", "services",
    "files", "about", "contact", "faq", "help", "news", "support", "blog", "wp-admin", "wp-content", "uploads",
    "media", "sitemap", "robots.txt", "api-docs", "status", "database", "vulnerabilities", "index"
]


scanned_results = []  # Global variable to store results

# Function to perform the directory brute force
def stream_brute_force_directories(url):
    global scanned_results
    scanned_results = []  # Clear previous results

    if not url.startswith("http"):
        url = "http://" + url

    for word in wordlist:
        full_url = f"{url}/{word}"
        try:
            response = requests.get(full_url)
            if response.status_code in [200, 403]:
                result = f"[+] Found: {full_url} (Status: {response.status_code})"
                scanned_results.append(result)  # Only append found URLs
        except requests.exceptions.RequestException as e:
            scanned_results.append(f"[!] Error accessing {full_url}: {e}")
        time.sleep(0.2)  # Simulate real-time processing

@app.route('/bruteforce', methods=['POST'])
def start_scan():
    data = request.json
    target_url = data.get('url', '')

    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # Start the brute force scan in a separate thread
    stream_brute_force_directories(target_url)

    return jsonify({"message": "Scan initiated. Use /bruteforce-stream to get results."}), 200

@app.route('/bruteforce-stream', methods=['GET'])
def stream_results():
    def event_stream():
        for result in scanned_results:
            yield f"data:{result}\n\n"
            time.sleep(0.1)  # Simulate streaming delay

    return Response(event_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
