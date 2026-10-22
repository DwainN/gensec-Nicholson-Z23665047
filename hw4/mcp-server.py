"""secops_toolkit: a small FastMCP server with security analysis tools.

The tools are plain functions so they can be unit tested directly. They are
registered with the MCP server below. Modeled on
04_MCP/01_sqlite/secure_sqlite_mcp_server.py from the course repo.

Usage:
    python mcp-server.py stdio   # for an MCP client that starts this process
    python mcp-server.py http    # streamable HTTP on 127.0.0.1:8080
"""

import hashlib
import ipaddress
import math
import re
import string
import sys

from fastmcp import FastMCP

mcp = FastMCP("secops_toolkit")

CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)
URL_RE = re.compile(r"\bhttps?://[^\s\"'<>()\[\]{}]+", re.IGNORECASE)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
HASH_RES = {
    "md5": re.compile(r"\b[a-fA-F0-9]{32}\b"),
    "sha1": re.compile(r"\b[a-fA-F0-9]{40}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
}
ALLOWED_HASHES = ("md5", "sha1", "sha256")


def _unique(items: list[str]) -> list[str]:
    """Return items without duplicates, keeping the first-seen order."""
    return list(dict.fromkeys(items))


def extract_iocs(text: str) -> dict[str, list[str]]:
    """Extract indicators of compromise (IOCs) from free text.

    Args:
        text: Any text, such as a report, log, or fetched web page.

    Returns:
        A dict with the keys cves, urls, ipv4, emails, md5, sha1 and sha256.
        Each value is a list of unique matches in first-seen order.
    """
    urls = [u.rstrip(".,;:!?") for u in URL_RE.findall(text)]
    ips = [ip for ip in IPV4_RE.findall(text) if _is_ipv4(ip)]
    result = {
        "cves": _unique([c.upper() for c in CVE_RE.findall(text)]),
        "urls": _unique(urls),
        "ipv4": _unique(ips),
        "emails": _unique(EMAIL_RE.findall(text)),
    }
    for name, pattern in HASH_RES.items():
        result[name] = _unique([h.lower() for h in pattern.findall(text)])
    return result


def _is_ipv4(value: str) -> bool:
    """Return True if value is a valid dotted-quad IPv4 address."""
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        return False
    return True


def cvss_to_severity(score: float) -> str:
    """Map a CVSS v3 base score to its qualitative severity rating.

    Ranges: 0.0 None, 0.1-3.9 Low, 4.0-6.9 Medium, 7.0-8.9 High,
    9.0-10.0 Critical.

    Args:
        score: The CVSS v3 base score.

    Returns:
        One of "None", "Low", "Medium", "High" or "Critical".

    Raises:
        ValueError: If score is not a number from 0 to 10.
    """
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("score must be a number from 0 to 10")
    if math.isnan(score) or not 0.0 <= score <= 10.0:
        raise ValueError("score must be a number from 0 to 10")
    if score == 0.0:
        return "None"
    if score < 4.0:
        return "Low"
    if score < 7.0:
        return "Medium"
    if score < 9.0:
        return "High"
    return "Critical"


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Hash text (UTF-8 encoded) and return the hex digest.

    Args:
        text: The text to hash.
        algorithm: One of "md5", "sha1" or "sha256". Default is "sha256".

    Returns:
        The lowercase hex digest.

    Raises:
        ValueError: If the algorithm is not allowed.
    """
    algo = algorithm.lower()
    if algo not in ALLOWED_HASHES:
        raise ValueError(f"algorithm must be one of {', '.join(ALLOWED_HASHES)}")
    return hashlib.new(algo, text.encode("utf-8")).hexdigest()


def password_strength(password: str) -> dict:
    """Estimate how strong a password is.

    The password itself is never logged or returned.

    Args:
        password: The password to check.

    Returns:
        A dict with length, the character classes used, an entropy
        estimate in bits (length * log2(pool size)), and a rating.
    """
    classes = {
        "lowercase": any(c in string.ascii_lowercase for c in password),
        "uppercase": any(c in string.ascii_uppercase for c in password),
        "digits": any(c in string.digits for c in password),
        "symbols": any(not c.isalnum() for c in password),
    }
    pool_sizes = {"lowercase": 26, "uppercase": 26, "digits": 10, "symbols": 33}
    pool = sum(size for name, size in pool_sizes.items() if classes[name])
    entropy = len(password) * math.log2(pool) if pool else 0.0

    if entropy < 28:
        rating = "Very weak"
    elif entropy < 36:
        rating = "Weak"
    elif entropy < 60:
        rating = "Moderate"
    elif entropy < 128:
        rating = "Strong"
    else:
        rating = "Very strong"

    return {
        "length": len(password),
        "character_classes": [name for name, used in classes.items() if used],
        "entropy_bits": round(entropy, 1),
        "rating": rating,
        "note": "Estimate only. Dictionary words and patterns make it weaker.",
    }


def incident_brief(cve_id: str) -> str:
    """Return a prompt that asks for a short incident brief about a CVE.

    Args:
        cve_id: The CVE id, for example CVE-2021-44228.

    Returns:
        The prompt text.
    """
    return (
        f"Write a short incident brief for {cve_id}. Use these headings:\n"
        "1. Summary: what the vulnerability is, in 2-3 sentences.\n"
        "2. Affected products: vendors, products and versions.\n"
        "3. Severity: the CVSS base score and its rating.\n"
        "4. Fix: patched versions or mitigations.\n"
        "Only use facts from the data you fetched. Say 'unknown' if a fact is missing."
    )


mcp.tool(extract_iocs)
mcp.tool(cvss_to_severity)
mcp.tool(hash_text)
mcp.tool(password_strength)
mcp.prompt(incident_brief)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("stdio", "http"):
        sys.exit("usage: python mcp-server.py [stdio|http]")
    if sys.argv[1] == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        mcp.run(transport="http", host="127.0.0.1", port=8080)
