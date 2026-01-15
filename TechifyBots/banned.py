from pyrogram import Client, filters, StopPropagation
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from config import ADMIN, DB_URI, DB_NAME

BAN_TEXT = "🚫 **ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.**"

# ================= DATABASE ================= #

class TechifyBots:
    def __init__(self):
        mongo_client = AsyncIOMotorClient(DB_URI)
        db = mongo_client[DB_NAME]
        self.banned_users = db["banned_users"]
        self.banned_channels = db["banned_channels"]

    async def ban(self, target_id: int, reason: str = None) -> bool:
        try:
            col = self.banned_users if target_id > 0 else self.banned_channels
            await col.update_one({"id": target_id}, {"$set": {"reason": reason}}, upsert=True)
            return True
        except:
            return False

    async def unban(self, target_id: int) -> bool:
        try:
            col = self.banned_users if target_id > 0 else self.banned_channels
            return (await col.delete_one({"id": target_id})).deleted_count > 0
        except:
            return False

    async def is_banned(self, target_id: int):
        col = self.banned_users if target_id > 0 else self.banned_channels
        return await col.find_one({"id": target_id})

tb = TechifyBots()

# ================= GLOBAL SEND GUARD ================= #

_original_send_message = Client.send_message
_original_send_document = Client.send_document
_original_send_video = Client.send_video
_original_send_sticker = Client.send_sticker
_original_send_photo = Client.send_photo
_original_send_audio = Client.send_audio
_original_send_animation = Client.send_animation

async def _guard_send(client, chat_id: int):
    if await tb.is_banned(chat_id):
        try:
            await _original_send_message(client, chat_id, BAN_TEXT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ 👨‍💻", user_id=int(ADMIN))]])
            )
        except:
            pass
        return False
    return True

async def send_message(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_message(self, chat_id, *a, **kw)

async def send_document(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_document(self, chat_id, *a, **kw)

async def send_video(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_video(self, chat_id, *a, **kw)

async def send_sticker(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_sticker(self, chat_id, *a, **kw)

async def send_photo(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_photo(self, chat_id, *a, **kw)

async def send_audio(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_audio(self, chat_id, *a, **kw)

async def send_animation(self, chat_id, *a, **kw):
    if not await _guard_send(self, chat_id):
        return
    return await _original_send_animation(self, chat_id, *a, **kw)

Client.send_message = send_message
Client.send_document = send_document
Client.send_video = send_video
Client.send_sticker = send_sticker
Client.send_photo = send_photo
Client.send_audio = send_audio
Client.send_animation = send_animation

# ================= INCOMING BAN CHECK ================= #

@Client.on_message(~filters.user(ADMIN) & ~filters.bot & ~filters.service, group=-2)
async def global_ban_checker(client: Client, m: Message):
    ban = None
    if m.from_user:
        ban = await tb.is_banned(m.from_user.id)
    if not ban and m.chat and m.chat.id < 0:
        ban = await tb.is_banned(m.chat.id)
    if not ban:
        return
    try:
        await m.delete()
    except:
        pass
    text = BAN_TEXT + (f"\n\n**Reason:** {ban['reason']}" if ban.get("reason") else "")
    try:
        await client.send_message(
            m.chat.id,
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ 👨‍💻", user_id=int(ADMIN))]]
            )
        )
    except:
        pass
    raise StopPropagation

# ================= ADMIN COMMANDS ================= #

@Client.on_message(filters.command("ban") & filters.private & filters.user(ADMIN))
async def ban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 2:
        return await m.reply("Usage: /ban user_id or channel_id [reason]")
    try:
        target_id = int(parts[1])
    except:
        return await m.reply("Invalid ID.")
    reason = parts[2] if len(parts) > 2 else None
    await tb.ban(target_id, reason)
    await m.reply(f"✅ **`{target_id}` banned.**")
    try:
        await c.send_message(target_id, BAN_TEXT + (f"\n\n**Reason:** {reason}" if reason else ""))
    except:
        pass

@Client.on_message(filters.command("unban") & filters.private & filters.user(ADMIN))
async def unban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.reply("Usage: /unban user_id or channel_id")
    try:
        target_id = int(parts[1])
    except:
        return await m.reply("Invalid ID.")
    if await tb.unban(target_id):
        await m.reply(f"✅ **`{target_id}` unbanned.**")
        try:
            await c.send_message(target_id, "✅ **ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.**")
        except:
            pass
    else:
        await m.reply("❌ ID was not banned.")

@Client.on_message(filters.command("banned") & filters.private & filters.user(ADMIN))
async def banned_cmd(client: Client, m: Message):
    users = await tb.banned_users.find().to_list(None)
    channels = await tb.banned_channels.find().to_list(None)
    if not users and not channels:
        return await m.reply("No users or channels are currently banned.")
    text = "🚫 Banned List:\n\n"
    for u in users:
        text += f"{u['id']} — {u.get('reason','No reason')}\n"
    for c in channels:
        text += f"{c['id']} — {c.get('reason','No reason')}\n"
    if len(text) <= 4000:
        return await m.reply(text)
    await client.send_document(m.chat.id, text.encode(), file_name="banned_list.txt")