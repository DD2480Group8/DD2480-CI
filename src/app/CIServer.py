from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        message = "Hello World!"
        self.wfile.write(message.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("Received POST request with data:", post_data.decode())
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Webhook received')

server = HTTPServer(('', 8008), SimpleHandler)
print('Server running on port 8008...')
server.serve_forever()