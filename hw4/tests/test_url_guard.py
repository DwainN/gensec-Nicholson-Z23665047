"""Unit tests for the URL guard in hw4/agent.py."""

import pytest

from agent import check_url


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://8.8.8.8/x",
        "http://localhost:8000/demo/injected_page.html",
        "http://app.localhost/",
        "http://127.0.0.1/",
        "http://[::1]/",
        "http://10.0.0.5/",
        "http://192.168.1.1/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http:///no-host",
    ],
)
def test_check_url_blocks_unsafe_urls(url):
    """Non-http(s), localhost, private and metadata URLs are blocked."""
    assert check_url(url) is not None


def test_check_url_allows_public_ip():
    """A public http(s) address is allowed."""
    assert check_url("https://8.8.8.8/") is None
