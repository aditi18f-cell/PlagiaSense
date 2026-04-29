from flask import Flask, render_template, request, jsonify
from utils.plagiarism import check_plagiarism

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():
    try:
        data = request.get_json()
        user_text = data.get("text", "")

        if not user_text.strip():
            return jsonify({"error": "No text provided"}), 400

        results = check_plagiarism(user_text)

        return jsonify(results)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    app.run(debug=True)