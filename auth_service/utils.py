from email.mime.text import MIMEText

import bcrypt, random, string
import smtplib

import jwt
from datetime import datetime, timedelta
from config import Config
from flask import request, jsonify

def create_jwt(user_id):
    payload = {
        "user_id": user_id,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def verify_jwt(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None



def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        data = verify_jwt(token)
        if not data:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user_id = data["user_id"]
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper



def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def otp_expired(otp_time):
    return datetime.utcnow() > otp_time + timedelta(minutes=5)



def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_FROM
        msg["To"] = to_email

        server = smtplib.SMTP("smtp-relay.brevo.com", 587)
        server.starttls()
        server.login("9c4404001@smtp-brevo.com", Config.BREVO_API_KEY)
        server.sendmail(Config.EMAIL_FROM, [to_email], msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print("SMTP Authentication failed:", e)
        return False

    except smtplib.SMTPException as e:
        print("SMTP error occurred:", e)
        return False

    except Exception as e:
        print("Unexpected error:", e)
        return False


