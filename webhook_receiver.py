import json
from http.server import BaseHTTPRequestHandler, HTTPServer

ALERT_FILE = "latest_webhook.json"

class WebhookHandler(BaseHTTPRequestHandler):
    def _send_response(self, code: int, body: str = ""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_response(400, json.dumps({"error": "Invalid JSON"}))
            return

        if "signal" not in payload or "ticker" not in payload:
            self._send_response(400, json.dumps({"error": "Required keys: ticker, signal"}))
            return

        with open(ALERT_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        self._send_response(200, json.dumps({"status": "ok", "received": payload}))

    def log_message(self, format, *args):
        return


def run(port: int = 5000):
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"Webhook receiver running on http://localhost:{port}/")
    print("Send TradingView alerts as POST JSON with keys: ticker, signal, timeframe, message")
    server.serve_forever()


if __name__ == "__main__":
    run()
