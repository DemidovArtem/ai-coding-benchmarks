"""Expose the pinned internal-only Sonar server on host loopback, without network changes."""

import json
from pathlib import Path
import selectors
import socket
import socketserver
import subprocess


CONTAINER = "ai-coding-sonar-server-1"
NETWORK = "ai-coding-sonar-internal"


def destination(container, network, image_id):
    if container.get("Image") != image_id or not container.get("State", {}).get("Running"):
        raise ValueError("The pinned Sonar server must be running")
    if network.get("Internal") is not True:
        raise ValueError("Sonar network must remain internal")
    networks = container["NetworkSettings"]["Networks"]
    if set(networks) != {NETWORK}:
        raise ValueError("Sonar server has unexpected network attachments")
    if networks[NETWORK]["NetworkID"] != network["Id"]:
        raise ValueError("Sonar network identity mismatch")
    return networks[NETWORK]["IPAddress"], 9000


class Relay(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            with socket.create_connection(self.server.destination, timeout=10) as upstream, selectors.DefaultSelector() as selector:
                upstream.settimeout(30)
                self.request.settimeout(30)
                selector.register(self.request, selectors.EVENT_READ, upstream)
                selector.register(upstream, selectors.EVENT_READ, self.request)
                while selector.get_map():
                    ready = selector.select(timeout=30)
                    if not ready:
                        return
                    for key, _ in ready:
                        data = key.fileobj.recv(65536)
                        if not data:
                            selector.unregister(key.fileobj)
                            key.data.shutdown(socket.SHUT_WR)
                        else:
                            key.data.sendall(data)
        except OSError:
            return


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    root = Path(__file__).resolve().parents[1]
    pins = json.loads((root / "sonar/setup_candidates.json").read_text())
    image_id = next(row["local_image_id"] for row in pins["images"] if row["role"] == "server")
    container = json.loads(subprocess.check_output(["docker", "inspect", CONTAINER]))[0]
    network = json.loads(subprocess.check_output(["docker", "network", "inspect", NETWORK]))[0]
    address = destination(container, network, image_id)
    with Server(("127.0.0.1", 9000), Relay) as server:
        server.destination = address
        print("Sonar relay listening on 127.0.0.1:9000; internal Docker network unchanged", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
