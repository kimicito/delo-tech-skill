#!/usr/bin/env python3
"""Upload files to Yandex Disk."""

import argparse
import os
import sys
import urllib.request
import urllib.parse
import json
import http.client

API_BASE = "https://cloud-api.yandex.net/v1/disk"

def get_token():
    """Read token from .env or environment."""
    env_path = os.path.expanduser("~/.openclaw/workspace/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("YANDEX_DISK_TOKEN="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("YANDEX_DISK_TOKEN")

def api_request(url, headers=None, method="GET", data=None):
    """Make authenticated API request."""
    token = get_token()
    if not token:
        print("ERROR: YANDEX_DISK_TOKEN not found.")
        print("Save it to ~/.openclaw/workspace/.env or set env var.")
        sys.exit(1)
    
    req_headers = {"Authorization": f"OAuth {token}"}
    if headers:
        req_headers.update(headers)
    
    req = urllib.request.Request(url, headers=req_headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        sys.exit(1)

def ensure_folder(path):
    """Create folder on Yandex Disk if it doesn't exist."""
    if not path or path == "/":
        return
    encoded = urllib.parse.quote(path)
    url = f"{API_BASE}/resources?path={encoded}"
    token = get_token()
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"}, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=60):
            print(f"  Folder ready: {path}")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"  Folder exists: {path}")
        else:
            print(f"  Folder error: {e.code}")
            raise

def upload_file(local_path, remote_folder=""):
    """Upload a single file to Yandex Disk."""
    filename = os.path.basename(local_path)
    if not os.path.exists(local_path):
        print(f"ERROR: File not found: {local_path}")
        return False
    
    remote_path = f"{remote_folder}/{filename}" if remote_folder else f"/{filename}"
    encoded = urllib.parse.quote(remote_path)
    
    # Get upload URL
    url = f"{API_BASE}/resources/upload?path={encoded}&overwrite=true"
    result = api_request(url)
    upload_url = result.get("href")
    
    if not upload_url:
        print("ERROR: No upload URL received")
        return False
    
    # Upload file content
    with open(local_path, "rb") as f:
        data = f.read()
    
    req = urllib.request.Request(upload_url, data=data, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            if resp.status in (200, 201, 202):
                print(f"  UPLOADED: {filename} -> {remote_path}")
                return True
    except urllib.error.HTTPError as e:
        print(f"  Upload failed: {e.code}")
        return False
    return False

def main():
    parser = argparse.ArgumentParser(description="Upload files to Yandex Disk")
    parser.add_argument("files", nargs="+", help="Local files to upload")
    parser.add_argument("--folder", default="", help="Remote folder path (e.g. /MarketPlays)")
    args = parser.parse_args()
    
    # Ensure folder exists
    if args.folder:
        ensure_folder(args.folder)
    
    success = 0
    for f in args.files:
        print(f"Uploading: {f}")
        if upload_file(f, args.folder):
            success += 1
    
    print(f"\nDone: {success}/{len(args.files)} files uploaded")

if __name__ == "__main__":
    main()
