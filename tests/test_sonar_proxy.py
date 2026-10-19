import copy
import socket
import socketserver
import threading
import unittest

from experiment.sonar_proxy import destination, NETWORK, Relay, Server


class ProxyTests(unittest.TestCase):
    def test_destination_requires_running_pinned_server_and_only_internal_network(self):
        network = {"Id":"network", "Internal":True}
        container = {"Image":"pinned", "State":{"Running":True}, "NetworkSettings":{"Networks":{
            NETWORK:{"NetworkID":"network", "IPAddress":"172.22.0.2"}}}}
        self.assertEqual(destination(container, network, "pinned"), ("172.22.0.2",9000))
        for mutation in ("image", "stopped", "network", "attachment"):
            value = copy.deepcopy(container)
            net = copy.deepcopy(network)
            if mutation == "image":
                value["Image"] = "other"
            elif mutation == "stopped":
                value["State"]["Running"] = False
            elif mutation == "network":
                net["Internal"] = False
            else:
                value["NetworkSettings"]["Networks"]["external"] = {}
            with self.assertRaises(ValueError):
                destination(value, net, "pinned")

    def test_relay_preserves_request_and_response_after_half_close(self):
        class Echo(socketserver.BaseRequestHandler):
            def handle(self):
                body = b""
                while data := self.request.recv(1024):
                    body += data
                self.request.sendall(body.upper())
        with Server(("127.0.0.1",0), Echo) as upstream, Server(("127.0.0.1",0), Relay) as proxy:
            proxy.destination = upstream.server_address
            threads = [threading.Thread(target=server.serve_forever,daemon=True) for server in (upstream,proxy)]
            for thread in threads:
                thread.start()
            try:
                with socket.create_connection(proxy.server_address) as connection:
                    connection.sendall(b"private request")
                    connection.shutdown(socket.SHUT_WR)
                    self.assertEqual(connection.recv(1024), b"PRIVATE REQUEST")
                    self.assertEqual(connection.recv(1024), b"")
            finally:
                proxy.shutdown()
                upstream.shutdown()
                for thread in threads:
                    thread.join()
