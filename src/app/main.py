from CIServer import SimpleHandler
from http.server import HTTPServer, BaseHTTPRequestHandler
from CIServer import run_server

"""Main entry point"""

server = run_server(8008)
server.serve_forever()


