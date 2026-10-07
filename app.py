from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

UPSTREAM_API = "https://free-fire-ob55-like-api.vercel.app/like"

# Keep the public UI and backend in sync.
ALLOWED_SERVERS = {"ind", "bd", "pk", "sg", "br", "us"}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/like")
def like_proxy():
    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "ind").strip().lower()

    if not uid:
        return jsonify({
            "status": 0,
            "error": "UID is required"
        }), 400

    if not uid.isdigit():
        return jsonify({
            "status": 0,
            "error": "UID must contain numbers only"
        }), 400

    # Prevent accidental very large input.
    if len(uid) > 20:
        return jsonify({
            "status": 0,
            "error": "Invalid UID"
        }), 400

    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Unsupported server"
        }), 400

    try:
        upstream = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=30
        )

        content_type = upstream.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            try:
                data = upstream.json()
            except ValueError:
                data = {
                    "status": 0,
                    "error": "Upstream returned invalid JSON"
                }
        else:
            # Some APIs return JSON without a JSON content-type.
            try:
                data = upstream.json()
            except ValueError:
                data = {
                    "status": 0,
                    "error": "Upstream returned an unexpected response"
                }

        # Preserve the upstream HTTP status when useful, but never leak
        # server-side exception details.
        status_code = upstream.status_code
        if status_code < 200 or status_code >= 600:
            status_code = 502

        return jsonify(data), status_code

    except requests.Timeout:
        return jsonify({
            "status": 0,
            "error": "Upstream API timed out. Please try again."
        }), 504

    except requests.RequestException:
        return jsonify({
            "status": 0,
            "error": "Unable to connect to the upstream API."
        }), 502

    except Exception:
        return jsonify({
            "status": 0,
            "error": "Unexpected server error."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
