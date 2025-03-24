from flask import Flask, jsonify
from flask_cors import CORS

from squats_routes import squats_bp
from pushups_routes import pushups_bp
from bicep_curls_routes import bicep_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Register the exercise blueprints
app.register_blueprint(squats_bp)
app.register_blueprint(pushups_bp)
app.register_blueprint(bicep_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "FitPal Backend Running!"})

if __name__ == "__main__":
    app.run(debug=False)
