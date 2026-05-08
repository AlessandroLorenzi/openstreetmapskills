#!/usr/bin/env python3
"""Obtain an OAuth 2.0 access token for the OSM API from the command line.

Prerequisites (one-time setup):
  1. Go to https://www.openstreetmap.org/oauth2/applications
  2. Click "Register new application"
  3. Fill in:
       Name:         (anything, e.g. "claude-osm-cli")
       Redirect URIs: urn:ietf:wg:oauth:2.0:oob
       Scopes:       check "write_api"
  4. Copy the Client ID (Client Secret is not needed for this flow)

Usage:
  python osm_auth.py <client_id>

Output:
  Prints the token to export as OSM_TOKEN
"""

import sys
import json
import hashlib
import base64
import secrets
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import urlopen, Request
from urllib.error import HTTPError

OSM_BASE = "https://www.openstreetmap.org"
AUTH_URL = f"{OSM_BASE}/oauth2/authorize"
TOKEN_URL = f"{OSM_BASE}/oauth2/token"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    client_id = sys.argv[1]
    verifier, challenge = pkce_pair()

    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "write_api",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    url = f"{AUTH_URL}?{urlencode(params)}"
    print(f"\nOpen this URL in your browser (opens automatically):\n\n  {url}\n")
    webbrowser.open(url)

    print("After authorising the app, OSM will show you a code.")
    code = input("Paste the code here: ").strip()

    data = urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": verifier,
    }).encode()

    req = Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(req) as r:
            resp = json.loads(r.read())
    except HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)

    token = resp.get("access_token")
    if not token:
        print(f"Unexpected response: {resp}")
        sys.exit(1)

    print(f"\nToken obtained! Export it with:\n\n  export OSM_TOKEN=\"{token}\"\n")
    print("Or add it to ~/.bashrc / ~/.zshrc to make it permanent.")


if __name__ == "__main__":
    main()
