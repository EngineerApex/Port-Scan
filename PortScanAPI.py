#PortScanAI
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import nmap
import socket
from flask import Flask, request, jsonify
import io
import sys
from flask_cors import CORS
import threading
import os

app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def port_scan():
    visited_urls = set()
    urllist = []
    url_join_sample = None
    print(f"Test 1 - works till here Nmap version: {os.popen('which nmap').read()} hellooooo")
    print(f"nmap.PortScanner().all_hosts(): {nmap.PortScanner().all_hosts()}")

    response = requests.get("https://www.yahoo.com")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tag = soup.find_all("a")
        urls = []   #this list will contain all the links that our code has found on the website
        for tag in a_tag:
            href = tag.get("href")
            if href is not None and href != "":
                urls.append(href)
        
        for urls2 in urls:
            if urls2 not in visited_urls:
                visited_urls.add(urls2)
                url_join = urljoin("https://www.yahoo.com", urls2)
                if "yahoo" in url_join:
                    urllist.append(url_join)
                    #print(url_join)
                    if not url_join_sample:  # Store the first matching URL
                        url_join_sample = url_join
                        #print(full_url)  # Print each matching URL
            else:
                pass
    else:
        print("[-] Failed to retrieve the webpage.")
    
    data = request.json
    target = data.get('ip', '')

    # Capture output using StringIO
    output_capture = io.StringIO()
    sys.stdout = output_capture  # Redirect print statements to the StringIO buffer

    try:
        # Validate IP address format
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return jsonify({"output": "[-] Invalid hostname or IP address"}), 400

        print(f"[+] Scanning the target: {ip} : Sample URL: {url_sample_output}")
        sys.stdout.flush()
        print("[+] This might take a while...")
        sys.stdout.flush()

        # Initialize the Nmap PortScanner
        nm = nmap.PortScanner()

        # Scan the target IP with specific arguments
        nm.scan(ip, arguments='-A -Pn -T4')

        if not nm.all_hosts():
            print("[-] No hosts were found.")
        else:
            for proto in nm[ip].all_protocols():
                print(f"\nProtocol: {proto}")
                lport = nm[ip][proto].keys()
                for port in sorted(lport):
                    state = nm[ip][proto][port]['state']
                    service = nm[ip][proto][port]['name']
                    version = nm[ip][proto][port].get('version', 'N/A')  # Get version if available
                    print(f"{port}/{proto} {state} {service} {version}")

    except Exception as e:
        print(f"[-] An error occurred: {e}")

    finally:
        # Reset stdout back to default
        sys.stdout = sys.__stdout__

    # Get the captured output as a string
    output = output_capture.getvalue()

    # Return the output as plain text
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True)
