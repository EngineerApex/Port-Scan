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
    print(f"Test 1 - works till here Nmap version: {os.popen('which nmap').read()} hellooooo")
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

        print(f"[+] Scanningggg the target: {ip} : nmap version - {nmap.PortScanner().nmap_version()}")
        sys.stdout.flush()
        print("[+] This might take a while...")
        sys.stdout.flush()

        # Initialize the Nmap PortScanner
        nm = nmap.PortScanner()

        # Scan the target IP with a simpler command
        nm.scan(ip)  # Use a simpler scan without arguments for debugging

        print(f"[DEBUG] Scan results: {nm[ip]}")  # Debug output to see what was returned

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
