#!/usr/bin/env python3
"""
Yandex Metrika OAuth flow helper.
Generates authorization URL for the user to get access token.
"""
import os
import urllib.parse

CLIENT_ID = os.getenv("YANDEX_METRIKA_CLIENT_ID", "d66120f045fd4783bcaa331c39513d32")
COUNTER_ID = os.getenv("YANDEX_METRIKA_COUNTER_ID", "92824982")

AUTH_URL = "https://oauth.yandex.ru/authorize"

params = {
    "response_type": "token",
    "client_id": CLIENT_ID,
    "scope": "metrika:read",
}

url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

print("=" * 60)
print("Yandex Metrika OAuth Authorization")
print("=" * 60)
print()
print("1. Open this URL in your browser:")
print(f"   {url}")
print()
print("2. Log in with your Yandex account")
print("3. Click 'Allow' / 'Разрешить'")
print("4. Browser will redirect to something like:")
print("   http://localhost:8000/callback#access_token=YOUR_TOKEN&token_type=bearer&expires_in=31536000")
print()
print("5. Copy the token (the long string after 'access_token=' and before '&')")
print()
print("6. Send me the token in this chat")
print()
print("=" * 60)
print()
print("Counter ID:", COUNTER_ID)
print("Client ID:", CLIENT_ID)
