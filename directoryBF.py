from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Wordlist of 50 common directories
wordlist = [
    "admin", "login", "user", "dashboard", "uploads", "assets", "css", "js", "images", "backup",
    "api", "config", "downloads", "docs", "includes", "lib", "public", "private", "test", "temp",
    "data", "scripts", "src", "themes", "vendor", "app", "cgi-bin", "server-status", "portal", "services",
    "files", "about", "contact", "faq", "help", "news", "support", "blog", "wp-admin", "wp-content", "uploads",
    "media", "sitemap", "robots.txt", "api-docs", "status", "database", "vulnerabilities", "index"
]


# Function to perform the directory brute force
def brute_force_directories(url):
    results = []
    # Ensure the URL starts with http:// or https://
    if not url.startswith("http"):
        url = "http://" + url

    for word in wordlist:
        # Build the full URL to check
        full_url = f"{url}/{word}"

        try:
            # Make a GET request to the URL
            response = requests.get(full_url)

            # Check if the directory exists (status code 200 or 403)
            if response.status_code == 200 or response.status_code == 403:
                result = f"[+] Found: {full_url} (Status: {response.status_code})"
                results.append(result)
            else:
                result = f"[-] Not Found: {full_url} (Status: {response.status_code})"
                results.append(result)

        except requests.exceptions.RequestException as e:
            error_message = f"[!] Error accessing {full_url}: {e}"
            results.append(error_message)

    return results


# Define the API endpoint for the directory brute force
@app.route('/bruteforce', methods=['POST'])
def brute_force_api():
    data = request.json
    target_url = data.get('url', '')

    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # Call the brute force function and get results
    results = brute_force_directories(target_url)

    # Return the results as a JSON response
    return jsonify({"output": "\n".join(results)})


if __name__ == '__main__':
    app.run(debug=True)
