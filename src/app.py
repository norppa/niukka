from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from db import init_db, get_record, set_record, del_record


def read_json(self):
    try:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        return json.loads(body) if body else {}
    except Exception as e:
        print(f"Failed to parse JSON body: {e}")
        return None


def send_json(self, data, status=200):
    body = json.dumps(data).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)


def send_status(self, status=200):
    self.send_response(status)
    self.end_headers()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Niukka API")
        
    def do_POST(self):
        body = read_json(self)
        if body is None:
            send_json(self, {"error": "invalid body"}, 400)
            return
        action = body.get("action")
        if action == "init":
            init_db()
            send_json(self, {"status": "OK"}, 200)
            return
        key = body.get("key")
        value = body.get("value")
        password = body.get("password")

        if not isinstance(key, str):
            send_json(self, {"error": "key is required"}, 400)
            return

        try:
            result = None
            match action:
                case "get":
                    result = get_record(key, password)
                    if result is None:
                        send_status(self, 404)
                        return
                case "set":
                    if not isinstance(value, str):
                        send_json(self, {"error": "value is required"}, 400)
                        return
                    set_record(key, value, password)
                    result = {"key": key, "value": value}
                case "del":
                    del_record(key, password)
                    result = {"key": key}
                case _:
                    send_json(self, {"error": "invalid action"}, 400)
                    return
            send_json(self, result, 200)
        except ValueError as e:
            send_status(self, 403)
            return

def run():
    server = HTTPServer(("127.0.0.1", 9001), Handler)
    print("🚀 minimal API running on http://127.0.0.1:9001")
    server.serve_forever()


if __name__ == "__main__":
    run()
