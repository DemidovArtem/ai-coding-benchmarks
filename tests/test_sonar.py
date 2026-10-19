from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from experiment.sonar import SonarClient, collect, normalize_measures, project_key


class SonarTests(unittest.TestCase):
    def fixture(self, status="SUCCESS", latest="analysis", rust=True):
        client = type("Client", (), {"token":"private-token"})()
        calls = []

        def get(path, **params):
            calls.append(path)
            if path == "/api/server/version":
                return "26.9.0.129388"
            if path == "/api/ce/task":
                return {"task":{"id":"task", "componentKey":"project", "status":status, "analysisId":"analysis"}}
            if path == "/api/project_analyses/search":
                return {"analyses":[{"key":latest}]}
            if path == "/api/metrics/search":
                return {"metrics":[{"key":"ncloc"},{"key":"complexity"}], "paging":{"total":2}}
            if path == "/api/measures/component":
                self.assertEqual(params["metricKeys"], "ncloc,complexity")
                return {"component":{"key":"project","measures":[{"metric":"ncloc","value":"10"}]}}
            if path == "/api/qualityprofiles/search":
                return {"profiles":[{"language":"rust"}] if rust else []}
            if path == "/api/plugins/installed":
                return {"plugins":[]}
            raise AssertionError(path)

        client.get = get
        return client, calls

    def test_completed_analysis_preserves_missing_metrics_as_null(self):
        client, calls = self.fixture()
        with tempfile.TemporaryDirectory() as tmp:
            result = collect(client,"task","project",Path(tmp)/"result","26.9.0.129388")
            self.assertTrue((Path(tmp)/"result/raw.json").exists())
        self.assertTrue(result["analysis_ok"])
        self.assertEqual(result["metrics"]["ncloc"], 10)
        self.assertIsNone(result["metrics"]["complexity"])
        self.assertIsNone(result["new_maintainability_issues"])
        self.assertEqual(calls[:2], ["/api/server/version", "/api/ce/task"])
        self.assertFalse(result["snapshot_binding_verified"])

    def test_failed_pending_superseded_or_unsupported_analysis_is_not_perfect_code(self):
        for kwargs in ({"status":"FAILED"},{"status":"IN_PROGRESS"},{"latest":"newer"},{"rust":False}):
            client, calls = self.fixture(**kwargs)
            with tempfile.TemporaryDirectory() as tmp:
                result = collect(client,"task","project",Path(tmp)/"result","26.9.0.129388",timeout=0)
            self.assertFalse(result["analysis_ok"])
            self.assertIsNone(result["metrics"]["ncloc"])
            self.assertEqual(result["failure_category"], "sonar_analysis_failure")

    def test_queue_is_waited_and_server_version_is_pinned(self):
        client, calls = self.fixture()
        original = client.get
        pending = True

        def get(path, **params):
            nonlocal pending
            if path == "/api/ce/task" and pending:
                pending = False
                calls.append(path)
                return {"task":{"id":"task","componentKey":"project","status":"PENDING"}}
            return original(path, **params)

        client.get = get
        with tempfile.TemporaryDirectory() as tmp, patch("experiment.sonar.time.sleep"):
            result = collect(client,"task","project",Path(tmp)/"ready","26.9.0.129388")
            self.assertTrue(result["analysis_ok"])
            self.assertEqual(calls[:3], ["/api/server/version", "/api/ce/task", "/api/ce/task"])
            result = collect(client,"task","project",Path(tmp)/"wrong-version","26.11.0.0")
            self.assertFalse(result["analysis_ok"])

    def test_missing_values_nonfinite_values_and_stable_unique_project_keys(self):
        self.assertIsNone(normalize_measures({})["ncloc"])
        with self.assertRaises(ValueError):
            normalize_measures({"component":{"measures":[{"metric":"ncloc","value":"NaN"}]}})
        self.assertEqual(project_key("trial", "a"*64), project_key("trial", "a"*64))
        self.assertNotEqual(project_key("trial", "a"*64), project_key("other", "a"*64))

    def test_raw_diagnostics_and_returned_metadata_redact_the_token(self):
        client, _ = self.fixture()
        original = client.get

        def get(path, **params):
            if path == "/api/server/version":
                return "private-token"
            return original(path, **params)

        client.get = get
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "result"
            result = collect(client,"task","project",directory,"26.9.0.129388")
            self.assertNotIn("private-token", json.dumps(result))
            self.assertNotIn("private-token", (directory/"raw.json").read_text())
            self.assertNotIn("private-token", (directory/"sonar.json").read_text())

    def test_transport_uses_bearer_without_proxy_or_redirect_leakage(self):
        observed = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                observed.append(self.headers.get("Authorization"))
                if self.path.startswith("/api/redirect"):
                    self.send_response(302)
                    self.send_header("Location", "/api/secret")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"ok":true}')

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with patch.dict("os.environ", {"HTTP_PROXY":"http://invalid:1"}):
                client = SonarClient(f"http://127.0.0.1:{server.server_port}", "private-token")
                self.assertEqual(client.get("/api/test"), {"ok":True})
                with self.assertRaisesRegex(RuntimeError, "HTTP 302"):
                    client.get("/api/redirect")
            self.assertEqual(observed, ["Bearer private-token", "Bearer private-token"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        for url in ("https://remote.example", "http://localhost:9000", "http://user:pass@127.0.0.1:9000"):
            with self.assertRaises(ValueError):
                SonarClient(url,"private-token")
        with self.assertRaises(ValueError):
            SonarClient("http://127.0.0.1:9000", "private\0token")
