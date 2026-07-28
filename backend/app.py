from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return {
        "project": "Hydroponics AI",
        "status": "Running"
    }


@app.route("/captures", methods=["POST"])
def captures():
    data = request.get_json()

    print("\nReceived from Raspberry Pi:")
    print(data)

    return jsonify({
        "status": "success",
        "received": data
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)