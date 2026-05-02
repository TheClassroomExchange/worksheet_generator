"""Run OAuth flow once and save token. Run this before pipeline.slides."""
import sys
sys.stdout.reconfigure(line_buffering=True)

from pipeline.slides import get_credentials

print("Starting OAuth flow...", flush=True)
print("A browser window should open. Sign in and grant Drive + Slides access.", flush=True)
print("If no browser opens automatically, copy the URL it prints below.", flush=True)
print("---", flush=True)

creds = get_credentials()

print("---", flush=True)
print(f"✓ Auth successful. Token saved.", flush=True)
print(f"  Valid: {creds.valid}", flush=True)
print(f"  Has refresh: {bool(creds.refresh_token)}", flush=True)
