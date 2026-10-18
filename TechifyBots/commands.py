import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, LOG_CHANNEL, PICS, NEW_REQ_MODE
from Script import text
from .database import tb

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    bot = await client.get_me()
    if await tb.get_user(message.from_user.id) is None:
        await tb.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            text.LOG.format(
                message.from_user.id,
                getattr(message.from_user, "dc_id", "N/A"),
                message.from_user.first_name or "N/A",
                f"@{message.from_user.username}" if message.from_user.username else "N/A",
                bot.username
            )
        )
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=text.START.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('⇆ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ⇆', url=f"https://telegram.me/{bot.username}?startgroup=true&admin=invite_users", style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton('ℹ️ 𝖠𝖻𝗈𝗎𝗍', callback_data='about'),
             InlineKeyboardButton('📚 𝖧𝖾𝗅𝗉', callback_data='help')],
            [InlineKeyboardButton('⇆ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 ⇆', url=f"https://telegram.me/{bot.username}?startchannel=true&admin=invite_users", style=enums.ButtonStyle.PRIMARY)]
            ])
        )

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    msg = await message.reply(text.GUIDE,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 𝖶𝖺𝗍𝖼𝗁 𝖳𝗎𝗍𝗈𝗋𝗂𝖺𝗅", url="https://youtu.be/_n3V0gFZMh8", style=enums.ButtonStyle.PRIMARY)]])
    )
    await asyncio.sleep(300)
    try:
        await msg.delete()
        await message.delete()
    except Exception:
        pass

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await tb.get_session(message.from_user.id)
    if user_data is None:
        return await show.edit("**To accept join requests, please /login first.**")
    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)
        await acc.connect()
    except:
        return await show.edit("**Your login session has expired. Use /logout first, then /login again.**")
    await show.edit("**Forward a message from your Channel or Group (with forward tag).\n\nMake sure your logged-in account is an admin there with full rights.**")
    fwd_msg = await client.listen(message.chat.id)
    if fwd_msg.forward_from_chat and fwd_msg.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = fwd_msg.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            return await show.edit("**Error: Ensure your account is admin in this Channel/Group with required rights.**")
    else:
        return await message.reply("**Message not forwarded from a valid Channel/Group.**")
    await fwd_msg.delete()
    msg = await show.edit("**Accepting all join requests... Please wait.**")
    try:
        total_approved = 0
        while True:
            join_requests = [req async for req in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
            await acc.approve_all_chat_join_requests(chat_id)
            total_approved += len(join_requests)
            await asyncio.sleep(1)
        await tb.record_approved_requests(
            total_approved,
            chat_id,
            getattr(info, "title", None) or str(chat_id),
            getattr(info, "type", "unknown"),
        )
        await msg.edit(f"**✅ Successfully accepted all join requests.**\n\n📊 Approved: `{total_approved:,}`")
    except Exception as e:
        await msg.edit(f"**An error occurred:** `{str(e)}`")

@Client.on_chat_join_request()
async def approve_new(client, m):
    await tb.record_approved_requests(
        0,
        m.chat.id,
        getattr(m.chat, "title", None) or str(m.chat.id),
        getattr(m.chat, "type", "unknown"),
    )
    if not NEW_REQ_MODE:
        return
    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        await tb.record_approved_requests(
            1,
            m.chat.id,
            getattr(m.chat, "title", None) or str(m.chat.id),
            getattr(m.chat, "type", "unknown"),
        )
        try:
            await client.send_message(
                m.from_user.id,
                f"{m.from_user.mention},\n\n𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝗌𝗍 𝖳𝗈 𝖩𝗈𝗂𝗇 {m.chat.title} 𝖧𝖺𝗌 𝖡𝖾𝖾𝗇 𝖠𝖼𝖼𝖾𝗉𝗍𝖾𝖽."
            )
        except:
            pass
    except Exception as e:
        print(str(e))
        pass
