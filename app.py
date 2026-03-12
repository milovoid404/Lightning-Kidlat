from flask import Flask, jsonify, request

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return "Welcome to my Flask API!"

# Student route
@app.route("/student")
def get_student():
    student = {
        "name": "BNJ",
        "grade": 10,
        "section": "ARDUINO"
    }
    return jsonify(student)

# Run locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
