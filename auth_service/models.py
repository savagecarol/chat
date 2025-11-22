from bson.objectid import ObjectId
from mongo_client import users_collection

class User:
    def __init__(self, email, password,is_verified=False, otp=None, otp_created=None,name=None):
        self.id = None
        self.email = email
        self.password = password
        self.name = name
        self.is_verified = is_verified
        self.otp = otp
        self.otp_created = otp_created

    def save(self):
        user_data = {
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "is_verified": self.is_verified,
            "otp": self.otp,
            "otp_created": self.otp_created
        }

        if hasattr(self, "id") and self.id:
            users_collection.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": user_data}
            )
            return self
        else:
            result = users_collection.insert_one(user_data)
            self.id = str(result.inserted_id)
            return self

    def update(self, **kwargs):
        users_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": kwargs}
        )
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def find_by_email(email):
        user_data = users_collection.find_one({"email": email})
        if user_data:
            user = User(
                email=user_data["email"],
                password=user_data["password"],
                name=user_data.get("name"),
                is_verified=user_data.get("is_verified", False),
                otp=user_data.get("otp"),
                otp_created=user_data.get("otp_created")
            )
            user.id = str(user_data["_id"])
            return user
        return None

    @staticmethod
    def find_by_id(user_id):
        try:
            user_data = users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                user = User(
                    email=user_data["email"],
                    password=user_data["password"],
                    name=user_data.get("name"),
                    is_verified=user_data.get("is_verified", False),
                    otp=user_data.get("otp"),
                    otp_created=user_data.get("otp_created")
                )
                user.id = str(user_data["_id"])
                return user
            return None
        except:
            return None