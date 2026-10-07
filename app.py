from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Official/Provided upstream endpoint
UPSTREAM_API = "https://free-fire-ob55-like-api.vercel.app/like"

# इस API के screenshot के अनुसार केवल India और Bangladesh
ALLOWED_SERVERS = {
    "ind",
    "bd"
}


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# HEALTH CHECK
# =========================
@app.route("/health")
def health():
    return jsonify({
        "status": 1,
        "message": "Free Fire Like Proxy is running"
    })


# =========================
# LIKE API PROXY
# =========================
@app.route("/api/like", methods=["GET"])
def like_proxy():

    # Get UID
    uid = request.args.get("uid", "").strip()

    # Get server and normalize it
    server = request.args.get("server_name", "ind").strip().lower()

    # -------------------------
    # UID VALIDATION
    # -------------------------
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
            "error": "Invalid UID length"
        }), 400

    # -------------------------
    # SERVER VALIDATION
    # -------------------------
    if server not in ALLOWED_SERVERS:
        return jsonify({
            "status": 0,
            "error": "Only India (ind) and Bangladesh (bd) are supported",
            "received_server": server
        }), 400

    # -------------------------
    # CALL UPSTREAM API
    # -------------------------
    try:

        response = requests.get(
            UPSTREAM_API,
            params={
                "uid": uid,
                "server_name": server
            },
            timeout=30
        )

        # Try JSON response
        try:
            data = response.json()

        except ValueError:

            return jsonify({
                "status": 0,
                "error": "Upstream API returned invalid JSON",
                "upstream_status": response.status_code,
                "upstream_response": response.text[:1000]
            }), 502

        # -------------------------
        # API REJECTED REQUEST
        # -------------------------
        if response.status_code != 200:

            return jsonify({
                "status": 0,
                "error": data.get(
                    "error",
                    "Upstream API request failed"
                ),
                "upstream_status": response.status_code,
                "upstream_response": data
            }), 502

        # -------------------------
        # API RETURNED ERROR
        # -------------------------
        if isinstance(data, dict) and data.get("status") == 0:

            return jsonify({
                "status": 0,
                "error": data.get(
                    "error",
                    "Invalid UID or server"
                ),

                # Diagnostic information
                "sent_uid": uid,
                "sent_server": server,

                # Exact API response
                "upstream_response": data
            })

        # -------------------------
        # SUCCESS
        # -------------------------
        return jsonify(data)

    # -------------------------
    # TIMEOUT
    # -------------------------
    except requests.exceptions.Timeout:

        return jsonify({
            "status": 0,
            "error": "Upstream API timed out"
        }), 504

    # -------------------------
    # CONNECTION ERROR
    # -------------------------
    except requests.exceptions.ConnectionError:

        return jsonify({
            "status": 0,
            "error": "Unable to connect to upstream API"
        }), 502

    # -------------------------
    # REQUEST ERROR
    # -------------------------
    except requests.exceptions.RequestException as e:

        return jsonify({
            "status": 0,
            "error": "API request failed",
            "details": str(e)
        }), 502

    # -------------------------
    # UNKNOWN ERROR
    # -------------------------
    except Exception as e:

        return jsonify({
            "status": 0,
            "error": "Internal server error",
            "details": str(e)
        }), 500


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
