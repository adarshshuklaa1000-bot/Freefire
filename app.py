from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://free-fire-ob55-like-api.vercel.app/like"


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
def like():

    uid = request.args.get("uid", "").strip()
    server = request.args.get("server_name", "ind").strip().lower()

    if not uid:
        return jsonify({
            "status": 0,
            "error": "UID is required"
        })

    if not uid.isdigit():
        return jsonify({
            "status": 0,
            "error": "UID must contain numbers only"
        })

    if server not in ["ind", "bd"]:
        return jsonify({
            "status": 0,
            "error": "Only India and Bangladesh servers are supported"
        })

    try:
        # EXACT API FORMAT FROM YOUR SCREENSHOT
        response = requests.get(
            API_URL,
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
                "raw_response": response.text[:1000]
            })

        # API ka original JSON response directly return karo
        return jsonify(data), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "status": 0,
            "error": "API request timed out"
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 0,
            "error": "Unable to connect to API",
            "details": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "status": 0,
            "error": "Server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
