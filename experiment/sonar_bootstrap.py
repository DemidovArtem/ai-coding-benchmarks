"""Secure the local pinned Sonar instance; credentials stay in ignored private storage."""

import argparse
import base64
import json
import os
from pathlib import Path
import secrets
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener, ProxyHandler, Request

from experiment.sonar import NoRedirect, SonarClient


VERSION = "26.9.0.129388"


def private_save(path, data):
    if path.is_symlink() or (path.exists() and path.stat().st_mode & 0o077):
        raise ValueError("Credential file must be private and must not be a symlink")
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as output:
        temporary = Path(output.name)
        try:
            json.dump(data, output)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def request(admin_password, path, **params):
    if not path.startswith("/api/") or "?" in path:
        raise ValueError("Invalid local API path")
    header = "Basic " + base64.b64encode(("admin:" + admin_password).encode()).decode()
    body = urlencode(params).encode() if params else None
    call = Request("http://127.0.0.1:9000" + path, data=body, headers={"Authorization":header})
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(call,timeout=15) as response:
            payload = response.read(10_000_001)
    except HTTPError as error:
        raise RuntimeError(f"Local Sonar HTTP {error.code} at {path}") from None
    except (URLError, TimeoutError):
        raise RuntimeError("Local Sonar API unavailable") from None
    if len(payload) > 10_000_000:
        raise ValueError("Local Sonar response exceeds budget")
    return json.loads(payload) if payload else {}


def bootstrap(path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.parent.stat().st_mode & 0o077:
        raise ValueError("Credential directory must have mode 0700")
    if path.exists() and (path.is_symlink() or path.stat().st_mode & 0o077):
        raise ValueError("Credential file must have mode 0600")
    data = json.loads(path.read_text()) if path.exists() else {
        "password":secrets.token_urlsafe(36), "token_name":"experiment-admin-" + secrets.token_hex(8)}
    private_save(path, data)
    if SonarClient("http://127.0.0.1:9000", "version-probe").get("/api/server/version") != VERSION:
        raise ValueError("Local Sonar server differs from the pin")
    if request(data["password"], "/api/authentication/validate").get("valid") is not True:
        if request("admin", "/api/authentication/validate").get("valid") is not True:
            raise RuntimeError("Neither saved nor initial admin credentials work; refusing reset")
        request("admin", "/api/users/change_password", login="admin", previousPassword="admin", password=data["password"])
    if request(data["password"], "/api/authentication/validate").get("valid") is not True:
        raise RuntimeError("New admin credential verification failed")
    if request("admin", "/api/authentication/validate").get("valid") is True:
        raise RuntimeError("Default admin password still works")
    if "token" not in data:
        # Recover safely if a prior process generated the named token but crashed before saving it.
        request(data["password"], "/api/user_tokens/revoke", name=data["token_name"])
        token = request(data["password"], "/api/user_tokens/generate", name=data["token_name"], type="USER_TOKEN")["token"]
        data["token"] = token
        private_save(path, data)
    client = SonarClient("http://127.0.0.1:9000", data["token"])
    if client.get("/api/authentication/validate").get("valid") is not True:
        raise RuntimeError("Saved admin token does not authenticate")
    profiles = client.get("/api/qualityprofiles/search", language="rust")
    plugins = client.get("/api/plugins/installed")
    return {"server_version":VERSION, "admin_password_changed":True, "token_verified":True,
            "credential_file":str(path), "quality_profiles":profiles, "plugins":plugins}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = bootstrap(args.credentials.absolute())
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2) + "\n")
        print(json.dumps({key:result[key] for key in ("server_version","admin_password_changed","token_verified")}))
    except (OSError, ValueError, RuntimeError, KeyError):
        raise SystemExit("Sonar bootstrap failed; credentials and API payloads suppressed") from None
