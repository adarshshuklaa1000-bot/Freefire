from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

UPSTREAM_API = "https://free-fire-ob55-like-api.vercel.app/like"

# API में region uppercase में भेजेंगे
ALLOWED_SERVERS = {
    "IND", "BD", "PK", "SG", "BR", "US"
}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "message": "Server is running"
    })


@app.get("/api/like")
def like_proxy():

    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "IND").strip().upper()

    # UID check
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

    if len(uid) < 5 or len(uid) > 20:
        return jsonify({
            "status": 0,
            "error": "Invalid UID"
        }), 400

    # Server check
    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Unsupported server"
        }), 400

    try:
        # Upstream API
        response = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=30
        )

        # JSON response
        try:
            data = response.json()
        except ValueError:
            return jsonify({
                "status": 0,
                "error": "API returned an invalid response",
                "raw": response.text[:500]
            }), 502

        return jsonify(data), response.status_code

    except requests.Timeout:
        return jsonify({
            "status": 0,
            "error": "API request timed out. Please try again."
        }), 504

    except requests.RequestException as e:
        return jsonify({
            "status": 0,
            "error": "Unable to connect to API."
        }), 502

    except Exception:
        return jsonify({
            "status": 0,
            "error": "Unexpected server error."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
