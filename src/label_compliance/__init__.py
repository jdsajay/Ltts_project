"""
Label Compliance System
========================
ISO-compliant medical device label verification.

Checks label PDFs against ISO standards (14607, 15223-1, etc.)
and generates annotated redline outputs showing compliance gaps.
"""

__version__ = "0.1.0"

# ── SSL bypass for corporate proxies / firewalls ──────────────────────
# Must run before any library (huggingface_hub, requests) is imported.
import os as _os
import ssl as _ssl

_os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
_os.environ["CURL_CA_BUNDLE"] = ""
_os.environ["REQUESTS_CA_BUNDLE"] = ""
_os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"

try:
    _ssl._create_default_https_context = _ssl._create_unverified_context
except AttributeError:
    pass

try:
    import urllib3 as _urllib3
    _urllib3.disable_warnings(_urllib3.exceptions.InsecureRequestWarning)
except (ImportError, AttributeError):
    pass
