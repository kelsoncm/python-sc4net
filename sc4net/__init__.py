
"""
sc4net
------

Atalhos para downloads HTTP(S) e FTP usando apenas a biblioteca padrão do Python, com utilitários para leitura de JSON e arquivos ZIP.

Principais funcionalidades:

- `get`: Faz download de conteúdo via HTTP(S) ou FTP.
- `get_json`: Baixa e decodifica JSON.
- `get_zip_content`: Baixa e extrai arquivos de dentro de ZIPs.
- `get_zip_csv_content`: Baixa e extrai CSVs de ZIPs.
- `post`/`post_json`: Envia requisições POST (com suporte a JSON).

Todos os métodos utilizam apenas módulos da biblioteca padrão, sem dependências externas.

Exemplo de uso:

    from sc4net import get_json
    dados = get_json('https://exemplo.com/dados.json')
    print(dados)

Licença: MIT
Autor: Kelson da Costa Medeiros
"""

import csv
import io
import json
from ftplib import FTP  # nosec B402
from http.client import HTTPException
from io import BytesIO
from typing import NoReturn, Optional, cast
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlparse
from urllib.request import Request, urlopen
from zipfile import ZipFile

def _unzip_content(data: bytes, file_id=0, encoding: str = "utf-8"):
    with ZipFile(BytesIO(data)) as zf:
        name = zf.namelist()[file_id] if isinstance(file_id, int) else file_id
        raw = zf.read(name)
    return raw.decode(encoding) if encoding else raw


def _unzip_csv_content(data: bytes, file_id=0, encoding: str = "utf-8", **kwargs):
    text = _unzip_content(data, file_id=file_id, encoding=encoding)
    return list(csv.DictReader(io.StringIO(text), **kwargs))


default_headers = {}


def _raise_http_exception(status, reason, url, headers=None) -> NoReturn:
    exc = HTTPException("%s - %s" % (status, reason))
    setattr(exc, "status", status)
    setattr(exc, "reason", reason)
    setattr(exc, "headers", headers or {})
    setattr(exc, "url", url)
    raise exc


def _merge_headers(headers):
    result = dict(default_headers)
    if headers:
        result.update(headers)
    return result


def _validate_web_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        _raise_http_exception(400, "Only http/https URLs are allowed", url)


def _ftp_get_with_stdlib(url, timeout=None) -> bytes:
    parsed = urlparse(url)
    host = parsed.hostname
    if host is None:
        _raise_http_exception(400, "Invalid FTP URL", url)

    port = parsed.port or 21
    username = unquote(parsed.username) if parsed.username else "anonymous"
    password = unquote(parsed.password) if parsed.password else "anonymous@"
    filepath = unquote(parsed.path.lstrip("/"))
    if filepath == "":
        _raise_http_exception(400, "FTP file path is required", url)

    try:
        with FTP() as ftp_client:  # nosec B321
            if timeout is None:
                ftp_client.connect(host=host, port=port)
            else:
                ftp_client.connect(host=host, port=port, timeout=float(timeout))
            ftp_client.login(user=username, passwd=password)
            output = BytesIO()
            ftp_client.retrbinary("RETR %s" % filepath, output.write)
            return output.getvalue()
    except Exception as exc:
        _raise_http_exception(502, str(exc), url)


def _http_get_with_stdlib(url, headers=None, timeout=None) -> bytes:
    _validate_web_url(url)
    request = Request(url, headers=_merge_headers(headers))
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310
            return response.read()
    except HTTPError as exc:
        _raise_http_exception(exc.code, exc.reason, url, dict(exc.headers or {}))
    except URLError as exc:
        _raise_http_exception(502, str(exc.reason), url)


def _build_post_payload(data, json_data, request_headers, encoding):

    if json_data is not None:
        payload = json.dumps(json_data).encode(encoding or "utf-8")
        if "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json"
        return payload

    if data is None:
        return None

    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode(encoding or "utf-8")
    if isinstance(data, dict):
        payload = urlencode(data, doseq=True).encode(encoding or "utf-8")
        if "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"
        return payload

    return str(data).encode(encoding or "utf-8")


def requests_get(
    url, headers=None, encoding: Optional[str] = "utf-8", decode=True, **kwargs
):
    """
    Download content from an HTTP(S) or FTP URL.

    :param url: str
        The URL to fetch (http, https, or ftp).
    :param headers: dict or None, optional
        Additional headers to send with the request.
    :param encoding: str or None, default "utf-8"
        Encoding to decode the response. If None, returns bytes.
    :param decode: bool, default True
        Whether to decode the response using the specified encoding.
    :param kwargs: dict
        Additional arguments, e.g., timeout.

    :returns:
        - str: Decoded content if decode is True and encoding is not None.
        - bytes: Raw content otherwise.

    :Examples:

        .. code-block:: python

            from sc4net import get
            text = get('https://example.com/data.txt')
            print(text)

            binary = get('ftp://ftp.example.com/file.zip', decode=False)
    """
    timeout = kwargs.get("timeout")
    if url.lower().startswith("ftp://"):
        byte_array_content = _ftp_get_with_stdlib(url, timeout=timeout)
    else:
        byte_array_content = _http_get_with_stdlib(
            url, headers=headers, timeout=timeout
        )

    return (
        byte_array_content.decode(encoding)
        if decode and encoding is not None
        else byte_array_content
    )


get = requests_get


def get_json(url, headers=None, encoding="utf-8", json_kwargs=None, **kwargs):
    """
    Download and decode JSON content from an HTTP(S) or FTP URL.

    :param url: str
        The URL to fetch.
    :param headers: dict or None, optional
        Additional headers to send with the request.
    :param encoding: str, default "utf-8"
        Encoding to decode the response.
    :param json_kwargs: dict or None, optional
        Extra arguments for json.loads.
    :param kwargs: dict
        Additional arguments, e.g., timeout.

    :returns:
        - dict or list: Parsed JSON content.

    :Examples:

        .. code-block:: python

            from sc4net import get_json
            data = get_json('https://example.com/data.json')
            print(data)
    """
    content = cast(
        str | bytes | bytearray, get(url, headers=headers, encoding=encoding, **kwargs)
    )
    if not isinstance(content, (str, bytes, bytearray)):  # pragma: no cover
        _raise_http_exception(500, "JSON content must be text or bytes", url)
    if isinstance(content, bytearray):  # pragma: no cover
        content = bytes(content)
    return json.loads(content, **(json_kwargs or {}))


def get_zip(url, headers=None, **kwargs):
    content = cast(
        bytes | bytearray, get(url, headers=headers, encoding=None, **kwargs)
    )
    if not isinstance(content, (bytes, bytearray)):  # pragma: no cover
        _raise_http_exception(500, "ZIP content must be bytes", url)
    if isinstance(content, bytearray):  # pragma: no cover
        content = bytes(content)
    return ZipFile(BytesIO(content))


def get_zip_content(url, headers=None, file_id=0, encoding="utf-8", **kwargs):
    """
    Download a ZIP file from a URL and extract the content of a file inside it.

    :param url: str
        The URL to fetch.
    :param headers: dict or None, optional
        Additional headers to send with the request.
    :param file_id: int or str, default 0
        Index or name of the file inside the ZIP to extract.
    :param encoding: str or None, default "utf-8"
        Encoding to decode the extracted file. If None, returns bytes.
    :param kwargs: dict
        Additional arguments, e.g., timeout.

    :returns:
        - str: Decoded file content if encoding is not None.
        - bytes: Raw file content otherwise.

    :Examples:

        .. code-block:: python

            from sc4net import get_zip_content
            text = get_zip_content('https://example.com/archive.zip', file_id=0)
            print(text)
    """
    content = cast(
        bytes | bytearray, get(url, encoding=None, headers=headers, **kwargs)
    )
    if not isinstance(content, (bytes, bytearray)):  # pragma: no cover
        _raise_http_exception(500, "ZIP content must be bytes", url)
    if isinstance(content, bytearray):  # pragma: no cover
        content = bytes(content)
    return _unzip_content(content, file_id=file_id, encoding=encoding)


def get_zip_csv_content(
    url, headers=None, file_id=0, encoding="utf-8", unzip_kwargs=None, **kwargs
):
    content = cast(
        bytes | bytearray, get(url, encoding=None, headers=headers, **kwargs)
    )
    if not isinstance(content, (bytes, bytearray)):  # pragma: no cover
        _raise_http_exception(500, "ZIP content must be bytes", url)
    if isinstance(content, bytearray):  # pragma: no cover
        content = bytes(content)
    return _unzip_csv_content(
        content, file_id=file_id, encoding=encoding, **(unzip_kwargs or {})
    )


def post(
    url,
    data=None,
    json_data=None,
    headers=None,
    encoding="utf-8",
    decode=True,
    **kwargs
):
    """
    Send a POST request to an HTTP(S) URL.

    :param url: str
        The URL to send the request to.
    :param data: dict, str, bytes or None, optional
        Data to send in the body (form or raw).
    :param json_data: dict or None, optional
        JSON data to send in the body.
    :param headers: dict or None, optional
        Additional headers to send.
    :param encoding: str, default "utf-8"
        Encoding for the request and response.
    :param decode: bool, default True
        Whether to decode the response.
    :param kwargs: dict
        Additional arguments, e.g., timeout.

    :returns:
        - str: Decoded response if decode is True and encoding is not None.
        - bytes: Raw response otherwise.

    :Examples:

        .. code-block:: python

            from sc4net import post
            response = post('https://example.com/api', data={'key': 'value'})
            print(response)
    """
    timeout = kwargs.get("timeout")
    request_headers = _merge_headers(headers)
    _validate_web_url(url)

    payload = _build_post_payload(data, json_data, request_headers, encoding)

    request = Request(url, data=payload, headers=request_headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310
            byte_array_content = response.read()
    except HTTPError as exc:
        _raise_http_exception(exc.code, exc.reason, url, dict(exc.headers or {}))
    except URLError as exc:
        _raise_http_exception(502, str(exc.reason), url)

    return (
        byte_array_content.decode(encoding)
        if decode and encoding is not None
        else byte_array_content
    )


def post_json(
    url,
    data=None,
    json_data=None,
    headers=None,
    encoding="utf-8",
    json_kwargs=None,
    **kwargs
):
    content = cast(
        str | bytes | bytearray,
        post(url, data, json_data, headers=headers, encoding=encoding, **kwargs),
    )
    if not isinstance(content, (str, bytes, bytearray)):  # pragma: no cover
        _raise_http_exception(500, "JSON content must be text or bytes", url)
    if isinstance(content, bytearray):  # pragma: no cover
        content = bytes(content)
    return json.loads(content, **(json_kwargs or {}))


def put(url, data=None, json_data=None, headers=None, encoding="utf-8", **kwargs):
    raise NotImplementedError()


def put_json(
    url,
    data=None,
    json_data=None,
    headers=None,
    encoding="utf-8",
    json_kwargs=None,
    **kwargs
):
    raise NotImplementedError()


def delete(url, headers=None, encoding="utf-8", decode=True, **kwargs):
    raise NotImplementedError()


def delete_json(url, headers=None, encoding="utf-8", json_kwargs=None, **kwargs):
    raise NotImplementedError()
