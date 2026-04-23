import os
import re
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

FILE_NOT_FOUND_ERROR_MESSAGE = "File not found"


dir_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets"))


def mock_ftpd():
    def get_free_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = get_free_port()
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(dir_path)
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "pyftpdlib based ftpd ready."
    server = FTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, port


class MockHttpServerRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super(MockHttpServerRequestHandler, self).__init__(request, client_address, server)

    def log_error(self, format, *args):
        pass

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parts = self.path.split("/")
        filepath = parts[len(parts) - 1]
        safe_filepath = os.path.basename(filepath)
        if safe_filepath in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9._-]+", safe_filepath):
            self.send_error(404, FILE_NOT_FOUND_ERROR_MESSAGE)
            return

        full_file_name = os.path.realpath(os.path.join(dir_path, safe_filepath))

        if os.path.commonpath([dir_path, full_file_name]) != dir_path:
            self.send_error(404, FILE_NOT_FOUND_ERROR_MESSAGE)
            return

        if not os.path.exists(full_file_name):
            self.send_error(404, FILE_NOT_FOUND_ERROR_MESSAGE)
            return

        self.send_response(200)
        self.end_headers()
        with open(full_file_name, "rb") as f:
            self.wfile.write(f.read())
        return

    def do_POST(self):
        parts = self.path.split("/")
        filepath = parts[len(parts) - 1]

        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length) if content_length > 0 else b""

        if filepath in ("echo", "echo.json"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_error(404, FILE_NOT_FOUND_ERROR_MESSAGE)
        return


def mock_httpd():
    def get_free_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = get_free_port()
    mock_http_server = HTTPServer(("localhost", port), MockHttpServerRequestHandler)
    thread = threading.Thread(target=mock_http_server.serve_forever)
    thread.daemon = True
    thread.start()
    return f"http://localhost:{port}", port
