"""
The MIT License (MIT)

Copyright (c) 2015 kelsoncm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from http.client import HTTPException
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

from sc4net import (
    delete,
    delete_json,
    get,
    get_json,
    get_zip,
    get_zip_content,
    get_zip_csv_content,
    post,
    post_json,
    put,
    put_json,
)

from .mocks import FILE_NOT_FOUND_ERROR_MESSAGE, mock_ftpd, mock_httpd

FILE01_CSV_EXPECTED = "codigo;nome\n1;um\n2;Dois\n3;três\n"
FILE01_CSV_EXPECTED_BINARY = b"codigo;nome\n1;um\n2;Dois\n3;tr\xc3\xaas\n"
FILE01_CSV_EXPECTED_LATIN1 = "codigo;nome\n1;um\n2;Dois\n3;trÃªs\n"

FILE02_JSON_EXPECTED = '["caça"]'
FILE02_JSON_EXPECTED_LATIN1 = '["caÃ§a"]'

FILE02_JSON_EXPECTED_BINARY = b'["ca\xc3\xa7a"]'

CSV_EXPECTED = [
    {"codigo": "1", "nome": "um"},
    {"codigo": "2", "nome": "Dois"},
    {"codigo": "3", "nome": "três"},
]
JSON_EXPECTED = ["caça"]
ZIP_EXPECTED = (
    b"PK\x03\x04\n\x00\x00\x00\x00\x00&z\xe9L\xad\rM\x07 \x00\x00\x00 \x00"
    b"\x00\x00\x08\x00\x1c\x00file.csvUT\t\x00\x03\xa8\xa6C[\xd6\xa6C[u"
    b"x\x0b\x00\x01\x04\xe8\x03\x00\x00\x04\xe8\x03\x00\x00codigo;nome\n1;um\n2"
    b";Dois\n3;tr\xc3\xaas\nPK\x01\x02\x1e\x03\n\x00\x00\x00\x00\x00&z\xe9L\xad\r"
    b"M\x07 \x00\x00\x00 \x00\x00\x00\x08\x00\x18\x00\x00\x00\x00\x00\x01\x00"
    b"\x00\x00\xb4\x81\x00\x00\x00\x00file.csvUT\x05\x00\x03\xa8\xa6C[ux\x0b"
    b"\x00\x01\x04\xe8\x03\x00\x00\x04\xe8\x03\x00\x00PK\x05\x06\x00\x00\x00\x00"
    b"\x01\x00\x01\x00N\x00\x00\x00b\x00\x00\x00\x00\x00"
)


class TestPythonBrfiedShortcutSyncHttp(TestCase):

    def setUp(self):
        http_root = TestPythonBrfiedShortcutSyncHttp.http_root
        self.file_not_found = http_root + "/file_not_found"
        self.file01_csv_url = http_root + "/file01.csv"
        self.file01_zip_url = http_root + "/file01.zip"
        self.file02_json_url = http_root + "/file02.json"
        self.file02_zip_url = http_root + "/file02.zip"
        self.echo_url = http_root + "/echo"
        self.echo_json_url = http_root + "/echo.json"

    @classmethod
    def setUpClass(cls):
        cls.http_root = mock_httpd()
        cls.ftpd = mock_ftpd()

    # @httpretty.activate
    def test_get(self):
        self.assertRaisesRegex(
            HTTPException, FILE_NOT_FOUND_ERROR_MESSAGE, get, self.file_not_found
        )

        try:
            self.assertIsNotNone(get(self.file_not_found))
        except Exception as exc:
            self.assertEqual(404, getattr(exc, "status", None))
            self.assertEqual("File not found", getattr(exc, "reason", None))
            self.assertTrue("Content-Type" in getattr(exc, "headers"))
            self.assertEqual(self.file_not_found, getattr(exc, "url", None))

        self.assertRaises(UnicodeDecodeError, get, self.file01_zip_url, None)

        self.assertEqual(FILE01_CSV_EXPECTED, get(self.file01_csv_url))
        self.assertEqual(
            FILE01_CSV_EXPECTED_BINARY, get(self.file01_csv_url, encoding=None)
        )
        self.assertEqual(
            FILE01_CSV_EXPECTED_LATIN1, get(self.file01_csv_url, encoding="latin1")
        )

        self.assertEqual(FILE02_JSON_EXPECTED, get(self.file02_json_url))
        self.assertEqual(
            FILE02_JSON_EXPECTED_BINARY, get(self.file02_json_url, encoding=None)
        )
        self.assertEqual(
            FILE02_JSON_EXPECTED_LATIN1, get(self.file02_json_url, encoding="latin1")
        )

        self.assertEqual(ZIP_EXPECTED, get(self.file01_zip_url, encoding=None))

    def test_get_json(self):
        self.assertEqual(JSON_EXPECTED, get_json(self.file02_json_url))

    def test_get_zip(self):
        self.assertIsInstance(get_zip(self.file01_zip_url), ZipFile)
        self.assertIsInstance(get_zip(self.file01_zip_url).filelist[0], ZipInfo)
        self.assertEqual("file.csv", get_zip(self.file01_zip_url).filelist[0].filename)
        self.assertEqual("file.csv", get_zip(self.file01_zip_url).filelist[0].filename)

    def test_get_zip_content(self):
        self.assertEqual(FILE01_CSV_EXPECTED, get_zip_content(self.file01_zip_url))

    def test_get_zip_csv_content(self):
        self.assertEqual(
            CSV_EXPECTED,
            get_zip_csv_content(self.file01_zip_url, unzip_kwargs={"delimiter": ";"}),
        )

    def test_get_zip_content_ftp(self):
        self.assertEqual(
            FILE01_CSV_EXPECTED, get_zip_content("ftp://localhost:2121/file01.zip")
        )

    def test_get_ftp(self):
        self.assertEqual("pong", get("ftp://localhost:2121/ping.txt"))

    def test_get_ftp_uses_stdlib(self):
        with patch("sc4net._ftp_get_with_stdlib", return_value=b"pong") as ftp_get:
            self.assertEqual("pong", get("ftp://localhost:2121/ping.txt"))
            ftp_get.assert_called_once()

    def test_post(self):
        self.assertEqual("a=1&b=2", post(self.echo_url, data={"a": "1", "b": "2"}))
        self.assertEqual("hello", post(self.echo_url, data="hello"))
        self.assertRaisesRegex(
            HTTPException, FILE_NOT_FOUND_ERROR_MESSAGE, post, self.file_not_found
        )

    def test_post_json(self):
        self.assertEqual(
            {"name": "kelson"},
            post_json(self.echo_json_url, json_data={"name": "kelson"}),
        )


class TestZEdgeCases(TestCase):
    """Covers edge-case branches not exercised by TestPythonBrfiedShortcutSyncHttp.

    Relies on the HTTP (port 1234) and FTP (port 2121) mock servers started by
    TestPythonBrfiedShortcutSyncHttp.setUpClass, which runs alphabetically first.
    """

    http_root = "http://localhost:1234"

    def setUp(self):
        self.file01_csv_url = self.http_root + "/file01.csv"
        self.echo_url = self.http_root + "/echo"
        self.echo_json_url = self.http_root + "/echo.json"

    # -- _merge_headers: branch where headers is not None (line 64) -----------

    def test_get_with_custom_headers(self):
        self.assertEqual(
            FILE01_CSV_EXPECTED,
            get(self.file01_csv_url, headers={"X-Test": "1"}),
        )

    # -- _validate_web_url: invalid scheme (line 71) --------------------------

    def test_get_invalid_url_scheme(self):
        self.assertRaises(HTTPException, get, "file:///etc/hosts")

    # -- _ftp_get_with_stdlib: hostname is None (line 78) ---------------------

    def test_ftp_no_hostname(self):
        self.assertRaises(HTTPException, get, "ftp:///ping.txt")

    # -- _ftp_get_with_stdlib: empty path (line 85) ---------------------------

    def test_ftp_empty_path(self):
        self.assertRaises(HTTPException, get, "ftp://localhost:2121/")

    # -- _ftp_get_with_stdlib: timeout branch (line 92) -----------------------

    def test_ftp_with_timeout(self):
        self.assertEqual("pong", get("ftp://localhost:2121/ping.txt", timeout=30))

    # -- _ftp_get_with_stdlib: except Exception (lines 97-98) ----------------

    def test_ftp_connection_error(self):
        with patch("sc4net.FTP", side_effect=Exception("forced ftp error")):
            self.assertRaises(HTTPException, get, "ftp://localhost:2121/ping.txt")

    # -- _http_get_with_stdlib: URLError (lines 109-110) ----------------------

    def test_http_url_error(self):
        from urllib.error import URLError

        with patch("sc4net.urlopen", side_effect=URLError("name resolution failed")):
            self.assertRaises(HTTPException, get, self.file01_csv_url)

    # -- _build_post_payload: bytes branch (line 125) -------------------------

    def test_post_with_bytes_data(self):
        self.assertEqual("raw", post(self.echo_url, data=b"raw"))

    # -- _build_post_payload: fallback str(data) (line 134) ------------------

    def test_post_with_fallback_data(self):
        self.assertEqual("42", post(self.echo_url, data=42))

    # -- post: URLError (lines 227-228) --------------------------------------

    def test_post_url_error(self):
        from urllib.error import URLError

        with patch("sc4net.urlopen", side_effect=URLError("unreachable")):
            self.assertRaises(HTTPException, post, self.echo_url, b"x")

    # -- Not implemented (lines 258, 270, 274, 278) --------------------------

    def test_put_not_implemented(self):
        self.assertRaises(NotImplementedError, put, self.echo_url)

    def test_put_json_not_implemented(self):
        self.assertRaises(NotImplementedError, put_json, self.echo_url)

    def test_delete_not_implemented(self):
        self.assertRaises(NotImplementedError, delete, self.echo_url)

    def test_delete_json_not_implemented(self):
        self.assertRaises(NotImplementedError, delete_json, self.echo_url)
