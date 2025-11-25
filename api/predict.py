from http.server import BaseHTTPRequestHandler
import json

# PERHATIKAN: Harus pakai class handler(BaseHTTPRequestHandler)
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_data = {"status": "Alive", "message": "GET Request Berhasil!"}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_POST(self):
        # Baca body request (opsional buat debug)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_data = {"status": "Alive", "message": "POST Request Berhasil!", "received": str(post_data)}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))