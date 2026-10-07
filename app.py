from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

UPSTREAM_API = "https://free-fire-ob55-like-api.vercel.app/like"

# इस API के अनुसार केवल India और Bangladesh
ALLOWED_SERVERS = {
    "ind",
    "bd"
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
@app.route("/api/test")
def api_test():
    uid = "18444886384"
    server = "ind"

    try:
        r = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=30
        )

        return jsonify({
            "sent_uid": uid,
            "sent_server": server,
            "api_status_code": r.status_code,
            "api_response": r.json()
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
def health():
    return jsonify({
        "status": 1,
        "message": "Server is working"
    })


@app.route("/api/like")
def like_proxy():

    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "ind").strip().lower()

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

    if len(uid) < 5 or len(uid) > 20:
        return jsonify({
            "status": 0,
            "error": "Invalid UID"
        }), 400

    # Server validation
    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Only India (IND) and Bangladesh (BD) servers are supported"
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
            return jsonify({
                "status": 0,
                "error": "API returned invalid JSON",
                "raw": response.text[:500]
            }), 502

        return jsonify(data), response.status_code

    except requests.exceptions.Timeout:

        return jsonify({
            "status": 0,
            "error": "API request timed out"
        }), 504

    except requests.exceptions.ConnectionError:

        return jsonify({
            "status": 0,
            "error": "Unable to connect to API"
        }), 502

    except requests.exceptions.RequestException:

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
