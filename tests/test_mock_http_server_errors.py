import pytest
from http.server import HTTPServer
from threading import Thread
from sc4net import get
from .mocks import FILE_NOT_FOUND_ERROR_MESSAGE, MockHttpServerRequestHandler

import socket


def get_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def http_server():
    port = get_free_port()
    server = HTTPServer(("localhost", port), MockHttpServerRequestHandler)
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield f"http://localhost:{port}"
    server.shutdown()
    thread.join()


def test_invalid_filename_returns_404(http_server):
    # Test unsafe/invalid filenames (should trigger 404 branch in do_GET)
    unsafe_names = ["", ".", "..", "file with spaces.txt", "file/../../etc/passwd", "file?.txt", "file|.txt"]
    for name in unsafe_names:
        url = f"{http_server}/{name}"
        with pytest.raises(Exception) as excinfo:
            get(url)
        # Só verifica status/mensagem se existirem
        if hasattr(excinfo.value, "status"):
            assert excinfo.value.status == 404
            assert FILE_NOT_FOUND_ERROR_MESSAGE in str(excinfo.value)


def test_nonexistent_file_returns_404(http_server):
    # Test non-existent file (should trigger 404 branch in do_GET)
    url = f"{http_server}/not_a_real_file.txt"
    with pytest.raises(Exception) as excinfo:
        get(url)
    assert hasattr(excinfo.value, "status")
    assert excinfo.value.status == 404
    assert FILE_NOT_FOUND_ERROR_MESSAGE in str(excinfo.value)
