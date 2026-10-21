import random
from pyrogram import Client, enums
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    WebAppInfo,
)
from Script import text
from config import PICS, VERSION, ADMIN, SOURCE_CODE
from .database import tb

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    bot = client.me.username
    if query.data == "start":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.START.format(query.from_user.mention)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⇆ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ⇆', url=f"https://telegram.me/{bot}?startgroup=true&admin=invite_users", style=enums.ButtonStyle.PRIMARY)],
                [InlineKeyboardButton('ℹ️ 𝖠𝖻𝗈𝗎𝗍', callback_data='about'),
                 InlineKeyboardButton('📚 𝖧𝖾𝗅𝗉', callback_data='help')],
                [InlineKeyboardButton('⇆ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 ⇆', url=f"https://telegram.me/{bot}?startchannel=true&admin=invite_users", style=enums.ButtonStyle.PRIMARY)]
            ])
        )

    elif query.data == "help":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.HELP.format(query.from_user.mention)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('👨‍💻 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋 👨‍💻', user_id=int(ADMIN))],
                [InlineKeyboardButton('↩️ 𝖡𝖺𝖼𝗄', callback_data='start', style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton('❌ 𝖢𝗅𝗈𝗌𝖾', callback_data='close', style=enums.ButtonStyle.DANGER)]
            ])
        )

    elif query.data == "about":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.ABOUT.format(VERSION)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('📂 𝖲𝗈𝗎𝗋𝖼𝖾 𝖢𝗈𝖽𝖾', url=SOURCE_CODE)],
                [InlineKeyboardButton('☕ 𝖣𝗈𝗇𝖺𝗍𝖾', callback_data='donate'),
                 InlineKeyboardButton('📊 𝖲𝗍𝖺𝗍𝗌', callback_data='stats')],
                [InlineKeyboardButton('↩️ 𝖡𝖺𝖼𝗄', callback_data='start', style=enums.ButtonStyle.PRIMARY)]
            ])
        )

    elif query.data == "stats":
        try:
            users = await tb.get_all_users()
            approved = await tb.get_total_approved_requests()
            chats = await tb.get_tracked_chats()
            channels = sum(1 for chat in chats if chat.get("chat_type") == "channel")
            groups = sum(1 for chat in chats if chat.get("chat_type") in ("group", "supergroup"))
            caption = text.STATS.format(approved=approved, channels=channels, groups=groups, users=len(users))
        except Exception as e:
            caption = f"❌ **Unable to load statistics.**\n\n`{e}`"

        await query.message.edit_media(
            InputMediaPhoto(media=random.choice(PICS), caption=caption),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('🌐 𝖶𝖾𝖻𝗌𝗂𝗍𝖾', web_app=WebAppInfo(url='https://anyaapprovebot.onrender.com'))],
                [InlineKeyboardButton('↩️ 𝖡𝖺𝖼𝗄', callback_data='about', style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton('❌ 𝖢𝗅𝗈𝗌𝖾', callback_data='close', style=enums.ButtonStyle.DANGER)]
            ])
        )

    elif query.data == "donate":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.DONATE
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('💳 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖳𝗁𝖾 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋', web_app=WebAppInfo(url='https://techifybots.vercel.app/pay'))],
                [InlineKeyboardButton('↩️ 𝖡𝖺𝖼𝗄', callback_data='about', style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton('❌ 𝖢𝗅𝗈𝗌𝖾', callback_data='close', style=enums.ButtonStyle.DANGER)]
            ])
        )

    elif query.data == "close":
        await query.message.delete()
