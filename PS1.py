import nmap
import socket
from flask import Flask, request, jsonify
import io
import sys
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/scan1', methods=['POST'])
def port_scan():
    # Print Nmap version and path for debugging
    print(f"Test 1 - works till here Nmap version: {os.popen('which nmap').read()} hellooooo")
    
    # Get the target IP address from the request
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

        print(f"[+] Scanningggg the target: {ip} also nmap version {nmap.PortScanner().nmap_version()} okkkkk")
        sys.stdout.flush()
        print("[+] This might take a while...")
        sys.stdout.flush()

        # Initialize the Nmap PortScanner
        nm = nmap.PortScanner()

        # Scan the target IP with modified arguments for better results
        nm.scan(ip, arguments='-A -Pn -T4')

        # Check if any hosts were found
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
        output_capture.write(f"[-] An error occurred: {e}\n")  # Log the error to output

    finally:
        # Reset stdout back to default
        sys.stdout = sys.__stdout__

    # Get the captured output as a string
    output = output_capture.getvalue()

    # Return the output as JSON
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True)
