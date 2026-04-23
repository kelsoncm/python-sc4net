import pytest
from sc4net import get, post

import sys

import_types = (Exception,)
if sys.version_info >= (3, 11):
    import_types = (Exception,)


def test_get_invalid_scheme():
    # Deve lançar HTTPException para file://
    with pytest.raises(Exception) as excinfo:
        get("file:///tmp/test.txt")
    assert hasattr(excinfo.value, "status")
    assert excinfo.value.status == 400
    assert "Only http/https URLs are allowed" in str(excinfo.value)


def test_post_invalid_scheme():
    # Deve lançar HTTPException para file://
    with pytest.raises(Exception) as excinfo:
        post("file:///tmp/test.txt")
    assert hasattr(excinfo.value, "status")
    assert excinfo.value.status == 400
    assert "Only http/https URLs are allowed" in str(excinfo.value)
