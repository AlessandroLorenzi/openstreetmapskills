#!/usr/bin/env python3
"""Ottieni un OAuth 2.0 access token per l'API OSM da riga di comando.

Passi preliminari (una volta sola):
  1. Vai su https://www.openstreetmap.org/oauth2/applications
  2. Clicca "Register new application"
  3. Compila:
       Name:         (qualsiasi, es. "claude-osm-cli")
       Redirect URIs: urn:ietf:wg:oauth:2.0:oob
       Scopes:       spunta "write_api"
  4. Copia il Client ID (non serve il Client Secret per questa flow)

Uso:
  python osm_auth.py <client_id>

Output:
  Stampa il token da esportare come OSM_TOKEN
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
    print(f"\nApri questo URL nel browser (si apre automaticamente):\n\n  {url}\n")
    webbrowser.open(url)

    print("Dopo aver autorizzato l'app, OSM mostrerà un codice.")
    code = input("Incolla qui il codice: ").strip()

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
        print(f"Errore {e.code}: {e.read().decode()}")
        sys.exit(1)

    token = resp.get("access_token")
    if not token:
        print(f"Risposta inattesa: {resp}")
        sys.exit(1)

    print(f"\nToken ottenuto! Esporta con:\n\n  export OSM_TOKEN=\"{token}\"\n")
    print("Oppure aggiungilo a ~/.bashrc / ~/.zshrc per renderlo permanente.")


if __name__ == "__main__":
    main()
