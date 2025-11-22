import jwt
from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# -----------------------------
# In-Memory Data
# -----------------------------
online_users = {}  # user_id → socket_id
waiting_queue = []  # list of user_ids
active_pairs = {}  # user_id → partner_user_id


# -----------------------------
# Validate JWT via Auth-Service
# -----------------------------
def validate_jwt(token):
    try:
        r = requests.get(
            "http://127.0.0.1:5001/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        if r.status_code != 200:
            return None

        return r.json()  # returns dict → {id, email, name}
    except:
        return None


# -----------------------------
# Socket: On Connect
# -----------------------------
@socketio.on("connect")
def handle_connect():
    token = request.args.get("token")
    if not token:
        print("Missing token")
        disconnect()
        return

    user = validate_jwt(token)
    if not user or "id" not in user:
        print("Invalid token")
        disconnect()
        return

    user_id = user["id"]

    online_users[user_id] = request.sid

    print(f"User {user_id} connected")

    emit("online_users", list(online_users.keys()), broadcast=True)


# -----------------------------
# Socket: On Disconnect
# -----------------------------
@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    user_to_remove = None

    # find user by sid
    for uid, socket_id in online_users.items():
        if socket_id == sid:
            user_to_remove = uid
            break

    if not user_to_remove:
        return

    print(f"User {user_to_remove} disconnected")

    # remove from online
    online_users.pop(user_to_remove, None)

    # remove from queue
    if user_to_remove in waiting_queue:
        waiting_queue.remove(user_to_remove)

    # handle active chat pair
    if user_to_remove in active_pairs:
        partner = active_pairs[user_to_remove]

        # remove both sides
        active_pairs.pop(user_to_remove, None)
        active_pairs.pop(partner, None)

        # notify partner
        partner_sid = online_users.get(partner)
        if partner_sid:
            socketio.emit("partner_disconnected", {}, room=partner_sid)

    emit("online_users", list(online_users.keys()), broadcast=True)


# -----------------------------
# User wants a chat partner
# -----------------------------
@socketio.on("join_queue")
def join_queue(data):
    token = data.get("token")
    user = validate_jwt(token)

    if not user or "id" not in user:
        return emit("error", {"msg": "Invalid token"})

    user_id = user["id"]

    # add to queue
    if user_id not in waiting_queue:
        waiting_queue.append(user_id)

    print("Queue:", waiting_queue)

    # match if 2 users available
    if len(waiting_queue) >= 2:
        u1 = waiting_queue.pop(0)
        u2 = waiting_queue.pop(0)

        active_pairs[u1] = u2
        active_pairs[u2] = u1

        print(f"Paired {u1} with {u2}")

        socketio.emit("matched", {"partner": u2}, room=online_users[u1])
        socketio.emit("matched", {"partner": u1}, room=online_users[u2])


# -----------------------------
# Messaging between partners
# -----------------------------
@socketio.on("message")
def relay_message(data):
    token = data.get("token")
    message = data.get("message")

    user = validate_jwt(token)

    if not user or "id" not in user:
        return emit("error", {"msg": "Invalid token"})

    user_id = user["id"]

    if user_id not in active_pairs:
        return emit("error", {"msg": "You have no partner"})

    partner = active_pairs[user_id]
    partner_sid = online_users.get(partner)

    if not partner_sid:
        return emit("error", {"msg": "Partner offline"})

    socketio.emit(
        "message",
        {"from": user_id, "text": message},
        room=partner_sid
    )


# -----------------------------
# Start Server
# -----------------------------
if __name__ == "__main__":
    print("Chat service running on http://127.0.0.1:5002")
    socketio.run(app, host="127.0.0.1", port=5002)


{
    "message": "Login successful",
    "name": "hiboy",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjkyMjIxOGY1ZGY4YTZlNjQ4OWRmMzM5IiwiaWF0IjoxNzYzODQ0NzMyfQ.y2nuyHoTvud-nCIosxJI1a-mEijojHYGL2Q6Cn90Mvk"
}


{
    "message": "Login successful",
    "name": "abcd",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjkyMWU4ODg1ZDA4ODA3YTRmNmNhYWY0IiwiaWF0IjoxNzYzODQ2NDY4fQ.roMneoSxQ4UbfepJAc0wXZgCiVLFAr2tij1IRrMFLP0"
}