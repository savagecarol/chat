from flask import Flask, request, jsonify, Blueprint

from utils import create_jwt
from config import Config
from models import User
from utils import hash_password, check_password, generate_otp, otp_expired, send_email
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

auth = Blueprint("auth", __name__, url_prefix="/auth")


@app.post("/register")
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return jsonify({"error": "Email & password required"}), 400

    user = User.find_by_email(email)
    hashed = hash_password(password)
    otp = generate_otp()

    if user is None:
        user = User(email=email, password=hashed, otp=otp, otp_created=datetime.utcnow(), name=name)

    else:
        if user.is_verified:
            return jsonify({"message": "Login successful", "name": user.name}), 200


    if not send_email(email, "Your OTP Code", f"Your OTP is {otp}"):
        return jsonify({"message": "email not sent"}), 400


    user.save()
    return jsonify({"message": "User registered. OTP sent to email."}), 200




# -----------------------
# STEP 2: VERIFY OTP
# -----------------------
@app.post("/verify")
def verify():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    user = User.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.is_verified:
        return jsonify({"message": "Already verified"}), 200

    if not otp or otp != user.otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if otp_expired(user.otp_created):
        return jsonify({"error": "OTP expired"}), 400

    user.update(is_verified=True, otp=None)

    return jsonify({"message": "User verified"}), 200


@app.post("/login")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not check_password(password, user.password):
        return jsonify({"error": "Invalid credentials"}), 400

    if not user.is_verified:
        return jsonify({"error": "User not verified"}), 400

    token = create_jwt(user.id)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "name": user.name
    }), 200


@app.post("/forgot")
def forgot():
    data = request.json
    email = data.get("email")

    user = User.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = generate_otp()
    user.update(otp=otp, otp_created=datetime.utcnow())

    send_email(email, "Password Reset OTP", f"Your OTP is {otp}")

    return jsonify({"message": "OTP sent for password reset"}), 200


@app.post("/reset_password")
def reset_password():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    user = User.find_by_email(email)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if otp != user.otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if otp_expired(user.otp_created):
        return jsonify({"error": "OTP expired"}), 400

    user.update(password=hash_password(new_password), otp=None)

    return jsonify({"message": "Password reset successful"}), 200

app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True, port=5001)