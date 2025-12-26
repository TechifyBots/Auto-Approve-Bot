import datetime
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from config import ADMIN, AUTH_CHANNELS, AUTH_REQ_CHANNELS, FSUB_EXPIRE, IS_FSUB
from TechifyBots.db import tb

def is_auth_req_channel(_, __, update):
    return update.chat.id in AUTH_REQ_CHANNELS

async def is_subscribed(bot: Client, user_id: int, expire_at):
    missing = []
    for channel_id in AUTH_CHANNELS:
        try:
            await bot.get_chat_member(channel_id, user_id)
        except UserNotParticipant:
            try:
                chat = await bot.get_chat(channel_id)
                invite = await bot.create_chat_invite_link(channel_id, expire_date=expire_at)
                missing.append((chat.title, invite.invite_link))
            except ChatAdminRequired:
                logging.error(f"Bot not admin in auth channel {channel_id}")
            except Exception:
                pass
        except Exception:
            pass
    return missing

async def is_req_subscribed(bot: Client, user_id: int, expire_at):
    missing = []
    for channel_id in AUTH_REQ_CHANNELS:
        if await tb.has_joined_channel(user_id, channel_id):
            continue
        try:
            chat = await bot.get_chat(channel_id)
            invite = await bot.create_chat_invite_link(channel_id, creates_join_request=True, expire_date=expire_at)
            missing.append((chat.title, invite.invite_link))
        except ChatAdminRequired:
            logging.error(f"Bot not admin in request channel {channel_id}")
        except Exception:
            pass
    return missing

async def get_fsub(bot: Client, message: Message) -> bool:
    user_id = message.from_user.id
    if user_id == ADMIN:
        return True
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=FSUB_EXPIRE) if FSUB_EXPIRE > 0 else None
    missing = []
    if AUTH_CHANNELS:
        missing.extend(await is_subscribed(bot, user_id, expire_at))
    if AUTH_REQ_CHANNELS:
        missing.extend(await is_req_subscribed(bot, user_id, expire_at))
    if not missing:
        return True
    bot_user = await bot.get_me()
    buttons = []
    for i in range(0, len(missing), 2):
        row = []
        for j in range(2):
            if i + j < len(missing):
                title, link = missing[i + j]
                row.append(InlineKeyboardButton(f"{i + j + 1}. {title}", url=link))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://telegram.me/{bot_user.username}?start=start")])
    await message.reply(f"**🎭 {message.from_user.mention}, You haven’t joined my channel yet.\nPlease join using the buttons below.**", reply_markup=InlineKeyboardMarkup(buttons))
    return False

@Client.on_chat_join_request(filters.create(is_auth_req_channel))
async def join_reqs(client: Client, message: ChatJoinRequest):
    await tb.add_join_req(message.from_user.id, message.chat.id)

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMIN), group=5)
async def del_requests(client: Client, message: Message):
    await tb.del_join_req()
    await message.reply("**⚙ Successfully join request cache deleted.**")

@Client.on_message(filters.private & ~filters.command() & ~filters.user(ADMIN), group=-10)
async def global_fsub_checker(client: Client, message: Message):
    if not IS_FSUB:
        return
    await get_fsub(client, message)

@Client.on_message(filters.private & ~filters.command() & ~filters.user(ADMIN), group=-2)
async def global_ban_checker(_, m: Message):
    if not m.from_user:
        return
    ban = await tb.is_user_banned(m.from_user.id)
    if not ban:
        return
    try:
        await m.delete()
    except Exception:
        pass
    text = "🚫 **You are banned from using this bot.**"
    if ban.get("reason"):
        text += f"\n\n**Reason:** {ban['reason']}"
    await m.reply_text(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 OWNER 👨‍💻",user_id=int(ADMIN))]]))
    await m.stop_propagation()

@Client.on_message(filters.command("ban") & filters.private & filters.user(ADMIN), group=5)
async def ban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 2:
        return await m.reply("Usage: /ban user_id [reason]")
    try:
        user_id = int(parts[1])
    except ValueError:
        return await m.reply("Invalid user ID.")
    reason = parts[2] if len(parts) > 2 else None
    if await tb.ban_user(user_id, reason):
        await m.reply(f"✅ **User `{user_id}` banned.**")
        try:
            msg = "🚫 You have been banned from using the bot."
            if reason:
                msg += f"\nReason: {reason}"
            await c.send_message(user_id, msg)
        except Exception:
            pass
    else:
        await m.reply("❌ Failed to ban user.")

@Client.on_message(filters.command("unban") & filters.private & filters.user(ADMIN), group=5)
async def unban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.reply("Usage: /unban user_id")
    try:
        user_id = int(parts[1])
    except ValueError:
        return await m.reply("Invalid user ID.")
    if await tb.unban_user(user_id):
        await m.reply(f"✅ **User `{user_id}` unbanned.**")
        try:
            await c.send_message(user_id,"✅ **You have been unbanned.**\n\nYou can now use the bot again.")
        except Exception:
            pass
    else:
        await m.reply("❌ User was not banned.")

@Client.on_message(filters.command("banned") & filters.private & filters.user(ADMIN), group=5)
async def banned_cmd(_, m: Message):
    users = await tb.banned_users.find().to_list(length=None)
    if not users:
        return await m.reply("No users are currently banned.")
    text = "🚫 **Banned Users:**\n\n"
    for u in users:
        text += f"• `{u['user_id']}` — {u.get('reason','No reason')}\n"
    await m.reply(text)

@Client.on_message(filters.private & ~filters.command() & ~filters.user(ADMIN), group=-1)
async def maintenance_blocker(_, m: Message):
    if not await tb.get_maintenance():
        return
    try:
        await m.delete()
    except Exception:
        pass
    await m.reply_text(f"<b>{m.from_user.mention},\n\nᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\n\n<blockquote>ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏ.</blockquote></b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 ᴏᴡɴᴇʀ 👨‍💻", user_id=int(ADMIN))]]))
    await m.stop_propagation()

@Client.on_message(filters.command("maintenance") & filters.user(ADMIN), group=5)
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
