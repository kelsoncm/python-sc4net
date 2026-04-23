sc4net
======

.. image:: https://img.shields.io/badge/GitHub-Repository-blue?logo=github
   :target: https://github.com/kelsoncm/python-sc4net
   :alt: GitHub Repository

.. image:: https://img.shields.io/badge/License-MIT-lemon.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/sc4net.svg
   :target: https://pypi.org/project/sc4net/
   :alt: Python

.. image:: https://github.com/kelsoncm/python-sc4net/actions/workflows/qa.yml/badge.svg
   :target: https://github.com/kelsoncm/python-sc4net/actions/workflows/qa.yml
   :alt: QA

.. image:: https://codecov.io/gh/kelsoncm/python-sc4net/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/kelsoncm/python-sc4net
   :alt: Coverage

.. image:: https://github.com/kelsoncm/python-sc4net/actions/workflows/publish.yml/badge.svg
   :target: https://github.com/kelsoncm/python-sc4net/actions/workflows/publish.yml
   :alt: Publish

.. image:: https://github.com/kelsoncm/python-sc4net/actions/workflows/docs.yml/badge.svg
   :target: https://kelsoncm.github.io/python-sc4net/
   :alt: Docs

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit


Network helpers for HTTP(S) and FTP downloads, with convenience JSON and ZIP readers.

Built entirely on Python stdlib — no third-party runtime dependencies.

Installation
------------

.. code-block::bash
   pip install sc4net

Requires Python 3.10 or later.


Quick start
-----------

.. code-block::python
   from sc4net import get, get_json, get_zip_csv_content

   # Simple HTTP GET (returns str)
   html = get("https://example.com/data.txt")

   # Fetch and parse JSON
   payload = get_json("https://api.example.com/items")

   # Download a ZIP and read a CSV from inside it
   rows = get_zip_csv_content(
      "https://example.com/report.zip",
      unzip_kwargs={"delimiter": ";"},
   )
   print(rows[:2])


Design goals
------------

========================= ============================================================================================
Goal                      Implementation
========================= ============================================================================================
Zero runtime dependencies Uses only `urllib`, `ftplib`, `zipfile`, `csv` from stdlib
Consistent error surface  All failures raise `http.client.HTTPException` with `.status`, `.reason`, `.url`, `.headers`
FTP and HTTP(S) unified   Same API regardless of protocol — prefix `ftp://` to use FTP
Modern Python             Tested against 3.10 – 3.14 on every commit
========================= ============================================================================================

Next steps
----------

.. toctree::
   :maxdepth: 1

   getting-started
   contribute
   sc4net
