from dotenv import load_dotenv

import os
from pymongo import MongoClient

load_dotenv()


class User:
    def __init__(self, db_id, tg_id, user_name, gender, age):
        self.db_id = db_id
        self.tg_id = tg_id
        self.user_name = user_name
        self.gender = gender
        self.age = age

    def dict(self):
        return {
            "db_id": self.db_id,
            "tg_id": self.tg_id,
            "user_name": self.user_name,
            "gender": self.gender,
            "age": self.age,
        }


class __UserModel():
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))

        db = client["telegram-profile-bot"]
        self.users = db["tg_users"]

    def insert_one(self, tg_id=None, user_name=None, gender=None, age=None):
        self.users.insert_one({
            "tg_id": tg_id,
            "user_name": user_name,
            "gender": gender,
            "age": age,
        })

    def is_user(self, tg_id):
        u = self.users.find_one({"tg_id": tg_id})
        return bool(u)

    def update(self, tg_id, user_name=None, gender=None, age=None):
        to_update = {}

        if user_name is not None:
            to_update.update({"user_name": user_name})
        if gender is not None:
            to_update.update({"gender": gender})
        if age is not None:
            to_update.update({"age": age})

        self.users.update_one({"tg_id": tg_id}, {'$set': to_update})
        return self.users.find_one({"tg_id": tg_id})

    def get_user(self, tg_id):
        return self.users.find_one({"tg_id": tg_id})

    def get_all(self):
        return self.users.find({})


UserModel = __UserModel()
