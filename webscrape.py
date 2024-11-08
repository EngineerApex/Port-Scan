from flask import Flask, request, jsonify, Response
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/webscrape', methods=['POST'])
def webscrape():
    # Extract JSON data from the request
    data = request.get_json()
    url = data.get("url")
    tag = data.get("keyword")

    if not url or not tag:
        return jsonify({"error": "Both URL and tag are required"}), 400

    try:
        # Make a request to the target URL
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(tag)  # Find all elements matching the provided tag

        # Extract the href attribute if it exists, otherwise return the element itself
        links = []
        for element in elements:
            href = element.get("href")
            if href:
                full_url = urljoin(url, href)
                links.append(full_url)
            else:
                links.append(str(element))

        # Return the links as a plain-text response
        return Response("\n".join(links), mimetype='text/plain')

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to scrape the website: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
