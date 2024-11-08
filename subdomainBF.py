from flask import Flask, request, Response, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Wordlist of 50 common subdomains
subdomains = [
    "www", "mail", "ftp", "webmail", "smtp", "admin", "blog", "store", "test", "api",
    "dev", "support", "cpanel", "forum", "help", "vpn", "news", "shop", "demo", "portal",
    "beta", "secure", "mobile", "staging", "cloud", "status", "docs", "www2", "intranet", "public",
    "ns1", "ns2", "dns", "files", "backup", "mx", "images", "cdn", "crm", "office",
    "accounts", "app", "billing", "download", "chat", "my", "static", "video", "search", "login"
]

scanned_results = []  # Global variable to store results

# Function to perform the subdomain brute force without printing "Not Found" URLs
def brute_force_subdomains(domain):
    global scanned_results
    scanned_results = []  # Clear previous results

    for subdomain in subdomains:
        # Build the full subdomain URL
        full_url = f"http://{subdomain}.{domain}"

        try:
            # Send a request to the subdomain
            response = requests.get(full_url)

            # Check if the subdomain is reachable (status code 200 or 403)
            if response.status_code == 200 or response.status_code == 403:
                result = f"[+] Found: {full_url} (Status: {response.status_code})"
                scanned_results.append(result)  # Append found subdomains
        except requests.exceptions.RequestException:
            pass  # Ignore requests that fail

# API endpoint to initiate the subdomain brute force scan
@app.route('/subd', methods=['POST'])
def start_scan():
    data = request.json
    target_domain = data.get('url', '')

    if not target_domain:
        return jsonify({"error": "Domain is required"}), 400

    # Start the brute force scan
    brute_force_subdomains(target_domain)
    return jsonify({"message": "Scan initiated"})

# API endpoint to stream results of the scan
@app.route('/subd-stream', methods=['GET'])
def stream_results():
    def event_stream():
        for result in scanned_results:
            yield f"data:{result}\n\n"
    
    return Response(event_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
