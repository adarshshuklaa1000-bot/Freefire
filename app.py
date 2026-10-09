from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# NEW API
UPSTREAM_API = "https://rishant-69.vercel.app/like"

ALLOWED_SERVERS = {"ind", "bd"}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": 1,
        "message": "Server is running"
    })


@app.route("/api/like", methods=["GET"])
def like_proxy():
    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "ind").strip().lower()

    if not uid:
        return jsonify({
            "status": 0,
            "error": "Please enter UID"
        }), 400

    if not uid.isdigit() or not 5 <= len(uid) <= 20:
        return jsonify({
            "status": 0,
            "error": "Invalid UID format"
        }), 400

    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Only India and Bangladesh are supported"
        }), 400

    try:
        response = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=25
        )

        try:
            data = response.json()
        except ValueError:
            return jsonify({
                "status": 0,
                "error": "API returned a non-JSON response",
                "upstream_status": response.status_code,
                "response": response.text[:500]
            }), 502

        # Preserve the upstream API's actual result.
        return jsonify(data), response.status_code

    except requests.Timeout:
        return jsonify({
            "status": 0,
            "error": "Upstream API timed out"
        }), 504

    except requests.RequestException:
        return jsonify({
            "status": 0,
            "error": "Could not connect to upstream API"
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

