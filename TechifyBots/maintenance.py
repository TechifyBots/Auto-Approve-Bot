from pyrogram import Client, filters, StopPropagation
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from config import ADMIN, DB_URI, DB_NAME

class TechifyBots:
    def __init__(self):
        mongo_client = AsyncIOMotorClient(DB_URI)
        db = mongo_client[DB_NAME]
        self.settings_col = db["settings"]

    async def get_maintenance(self) -> bool:
        data = await self.settings_col.find_one({"_id": "maintenance"})
        return data.get("status", False) if data else False

    async def set_maintenance(self, status: bool):
        await self.settings_col.update_one({"_id": "maintenance"}, {"$set": {"status": status}}, upsert=True)

tb = TechifyBots()

@Client.on_message(filters.private & ~filters.user(ADMIN) & ~filters.bot & ~filters.service & ~filters.me, group=-1)
async def maintenance_blocker(_, m: Message):
    if not await tb.get_maintenance():
        return
    try:
        await m.delete()
    except:
        pass
    await m.reply_text(f"{m.from_user.mention},\n\nᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\n\nᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏ.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ 👨‍💻", user_id=int(ADMIN))]]))
    raise StopPropagation

@Client.on_message(filters.command("maintenance") & filters.user(ADMIN))
async def maintenance_cmd(_, m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        return await m.reply("Usage: /maintenance [on/off]")
    status = args[1].lower()
    if status == "on":
        if await tb.get_maintenance():
            return await m.reply("⚠️ Maintenance mode is already enabled.")
        await tb.set_maintenance(True)
        return await m.reply("✅ Maintenance mode **enabled**.")
    if status == "off":
        if not await tb.get_maintenance():
            return await m.reply("⚠️ Maintenance mode is already disabled.")
        await tb.set_maintenance(False)
        return await m.reply("❌ Maintenance mode **disabled**.")
    await m.reply("Invalid status. Use 'on' or 'off'.")