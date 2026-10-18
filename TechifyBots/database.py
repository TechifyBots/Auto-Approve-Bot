from typing import Any
from config import DB_URI, DB_NAME
from motor import motor_asyncio
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

client = motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

class Techifybots:
    def __init__(self):
        self.users = db["users"]
        self.stats = db["bot_stats"]
        self.tracked_chats = db["tracked_chats"]
        self.cache: dict[int, dict[str, Any]] = {}

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


    async def record_approved_requests(self, count: int, chat_id: int, title: str, chat_type: str) -> None:
        """Persist successful approvals and remember chats where requests were handled."""
        try:
            if count > 0:
                await self.stats.update_one(
                    {"_id": "global"},
                    {"$inc": {"total_approved": int(count)}},
                    upsert=True,
                )
            await self.tracked_chats.update_one(
                {"chat_id": int(chat_id)},
                {"$set": {
                    "chat_id": int(chat_id),
                    "title": title or str(chat_id),
                    "chat_type": str(getattr(chat_type, "value", chat_type)).lower().split(".")[-1],
                    "updated_at": __import__("datetime").datetime.utcnow(),
                }},
                upsert=True,
            )
        except Exception as e:
            print("Error recording approved requests:", e)

    async def get_total_approved_requests(self) -> int:
        try:
            doc = await self.stats.find_one({"_id": "global"})
            return int(doc.get("total_approved", 0)) if doc else 0
        except Exception as e:
            print("Error getting approved request total:", e)
            return 0

    async def get_tracked_chats(self) -> list[dict[str, Any]]:
        try:
            return await self.tracked_chats.find().to_list(length=None)
        except Exception as e:
            print("Error getting tracked chats:", e)
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

tb = Techifybots()
