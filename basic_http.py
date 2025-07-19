# save as delay_server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class DelayedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Wait 5 seconds BEFORE sending response
        time.sleep(5)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Response after 5 seconds\n")

        # To keep connection alive after sending (optional)
        # time.sleep(5)

if __name__ == "__main__":
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, DelayedHandler)
    print("Serving on port 8080...")
    httpd.serve_forever()
