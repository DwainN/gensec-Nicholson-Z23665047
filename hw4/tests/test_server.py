"""Unit tests for the plain functions in hw4/mcp-server.py."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

# The file name has a hyphen, so it cannot be imported with a normal import.
_PATH = Path(__file__).resolve().parent.parent / "mcp-server.py"
_spec = importlib.util.spec_from_file_location("mcp_server", _PATH)
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)


def test_extract_iocs_finds_each_type():
    """Every IOC type is found once, with no duplicates."""
    md5 = hashlib.md5(b"x").hexdigest()
    sha1 = hashlib.sha1(b"x").hexdigest()
    sha256 = hashlib.sha256(b"x").hexdigest()
    text = (
        f"See cve-2021-44228 and CVE-2021-44228 at https://example.com/a. "
        f"Host 10.0.0.5 and bad 999.1.1.1, mail soc@example.org. "
        f"{md5} {sha1} {sha256}"
    )
    iocs = server.extract_iocs(text)
    assert iocs["cves"] == ["CVE-2021-44228"]
    assert iocs["urls"] == ["https://example.com/a"]
    assert iocs["ipv4"] == ["10.0.0.5"]
    assert iocs["emails"] == ["soc@example.org"]
    assert iocs["md5"] == [md5]
    assert iocs["sha1"] == [sha1]
    assert iocs["sha256"] == [sha256]


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0, "None"), (0.1, "Low"), (3.9, "Low"), (4.0, "Medium"), (6.9, "Medium"),
     (7.0, "High"), (8.9, "High"), (9.0, "Critical"), (10, "Critical")],
)
def test_cvss_to_severity_ranges(score, expected):
    """Scores map to the CVSS v3 severity ranges."""
    assert server.cvss_to_severity(score) == expected


@pytest.mark.parametrize("score", [-0.1, 10.1, float("nan"), True])
def test_cvss_to_severity_rejects_bad_scores(score):
    """Scores outside 0-10 are rejected."""
    with pytest.raises(ValueError):
        server.cvss_to_severity(score)


def test_hash_text_matches_hashlib():
    """Allowed algorithms match hashlib; the default is sha256."""
    assert server.hash_text("abc") == hashlib.sha256(b"abc").hexdigest()
    assert server.hash_text("abc", "MD5") == hashlib.md5(b"abc").hexdigest()


def test_hash_text_rejects_other_algorithms():
    """Algorithms outside the allow list are rejected."""
    with pytest.raises(ValueError):
        server.hash_text("abc", "sha512")


def test_password_strength_does_not_return_password():
    """The result rates the password and never contains it."""
    secret = "Summer2024!"
    result = server.password_strength(secret)
    assert result["length"] == 11
    assert result["character_classes"] == ["lowercase", "uppercase", "digits", "symbols"]
    assert result["rating"] == "Strong"
    assert secret not in repr(result)


def test_password_strength_empty():
    """An empty password has zero entropy."""
    result = server.password_strength("")
    assert result["entropy_bits"] == 0.0
    assert result["rating"] == "Very weak"


def test_incident_brief_has_all_sections():
    """The prompt names the CVE and asks for all four sections."""
    text = server.incident_brief("CVE-2021-44228")
    assert "CVE-2021-44228" in text
    for word in ("Summary", "Affected products", "Severity", "Fix"):
        assert word in text
