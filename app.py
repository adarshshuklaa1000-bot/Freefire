from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

UPSTREAM_API = "https://free-fire-ob55-like-api.vercel.app/like"

ALLOWED_SERVERS = {
    "IND", "BD", "PK", "SG", "BR", "US"
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": 1,
        "message": "Proxy is working"
    })


@app.route("/api/like")
def like():
    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "IND").strip().upper()

    # UID validation
    if not uid:
        return jsonify({
            "status": 0,
            "error": "Please enter UID"
        }), 400

    if not uid.isdigit():
        return jsonify({
            "status": 0,
            "error": "UID must contain numbers only"
        }), 400

    if not 5 <= len(uid) <= 20:
        return jsonify({
            "status": 0,
            "error": "Invalid UID length"
        }), 400

    # Server validation
    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Invalid server"
        }), 400

    try:
        response = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=30
        )

        try:
            data = response.json()
        except ValueError:
            data = {
                "status": 0,
                "error": "API returned invalid JSON",
                "response": response.text[:500]
            }

        return jsonify(data), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "status": 0,
            "error": "API timeout"
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "status": 0,
            "error": "Could not connect to API"
        }), 502

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 0,
            "error": "API request failed"
        }), 502

    except Exception:
        return jsonify({
            "status": 0,
            "error": "Internal server error"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
