import datetime
from typing import Any
from config import DB_URI, DB_NAME, FSUB_EXPIRE
from motor import motor_asyncio
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

client = motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

class Techifybots:
    def __init__(self):
        self.users = db["users"]
        self.settings_col = db["settings"]
        self.join_requests = db["join_requests"]
        self.banned_users = db["banned_users"]
        self.cache: dict[int, dict[str, Any]] = {}

        if FSUB_EXPIRE > 0:
            self.join_requests.create_index(
                "created_at",
                expireAfterSeconds=FSUB_EXPIRE * 60
            )

    async def add_user(self, user_id: int, name: str) -> dict[str, Any] | None:
        try:
            user = {"user_id": int(user_id), "name": name}
            saved = await self.users.find_one_and_update(
                {"user_id": user["user_id"]},
                {"$set": user},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            if saved:
                self.cache[user["user_id"]] = saved
            return saved
        except DuplicateKeyError:
            existing = await self.users.find_one({"user_id": int(user_id)})
            if existing:
                self.cache[int(user_id)] = existing
            return existing
        except Exception as e:
            print("Error in add_user:", e)
            return None

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        try:
            if user_id in self.cache:
                return self.cache[user_id]
            user = await self.users.find_one({"user_id": int(user_id)})
            if user:
                self.cache[user_id] = user
            return user
        except Exception as e:
            print("Error in get_user:", e)
            return None

    async def set_session(self, user_id: int, session: Any) -> bool:
        try:
            result = await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"session": session}}
            )
            if user_id in self.cache:
                self.cache[user_id]["session"] = session
            return result.modified_count > 0
        except Exception as e:
            print("Error in set_session:", e)
            return False

    async def get_session(self, user_id: int) -> Any | None:
        try:
            user = await self.get_user(user_id)
            return user.get("session") if user else None
        except Exception as e:
            print("Error in get_session:", e)
            return None

    async def get_all_users(self) -> list[dict[str, Any]]:
        try:
            users: list[dict[str, Any]] = []
            async for user in self.users.find():
                users.append(user)
            return users
        except Exception as e:
            print("Error in get_all_users:", e)
            return []

    async def delete_user(self, identifier: int | str | ObjectId) -> bool:
        try:
            query = {}
            if isinstance(identifier, int):
                query = {"user_id": identifier}
                self.cache.pop(identifier, None)
            elif isinstance(identifier, (str, ObjectId)):
                query = {"_id": ObjectId(identifier)} if isinstance(identifier, str) else {"_id": identifier}
                doc = await self.users.find_one(query)
                if doc and "user_id" in doc:
                    self.cache.pop(int(doc["user_id"]), None)
            else:
                return False
            result = await self.users.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print("Error in delete_user:", e)
            return False

    async def get_maintenance(self) -> bool:
        data = await self.settings_col.find_one({"_id": "maintenance"})
        return data.get("status", False) if data else False

    async def set_maintenance(self, status: bool):
        await self.settings_col.update_one(
            {"_id": "maintenance"},
            {"$set": {"status": status}},
            upsert=True
        )

    async def add_join_req(self, user_id: int, channel_id: int):
        await self.join_requests.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"channels": channel_id},
                "$setOnInsert": {"created_at": datetime.datetime.utcnow()}
            },
            upsert=True
        )

    async def has_joined_channel(self, user_id: int, channel_id: int) -> bool:
        doc = await self.join_requests.find_one({"user_id": user_id})
        return bool(doc and channel_id in doc.get("channels", []))

    async def del_join_req(self):
        await self.join_requests.drop()

    async def ban_user(self, user_id: int, reason: str | None = None) -> bool:
        try:
            await self.banned_users.update_one(
                {"user_id": user_id},
                {"$set": {"reason": reason}},
                upsert=True
            )
            return True
        except Exception:
            return False

    async def unban_user(self, user_id: int) -> bool:
        try:
            result = await self.banned_users.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def is_user_banned(self, user_id: int):
        return await self.banned_users.find_one({"user_id": user_id})

tb = Techifybots()