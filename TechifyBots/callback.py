import random
from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from Script import text
from config import ADMIN, PICS

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
                [InlineKeyboardButton('📢 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url='https://telegram.me/Techifybots'),
                 InlineKeyboardButton('💬 𝖲𝗎𝗉𝗉𝗈𝗋𝗍', url='https://telegram.me/TechifySupport')],
                [InlineKeyboardButton('↩️ 𝖡𝖺𝖼𝗄', callback_data="start", style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton('❌ 𝖢𝗅𝗈𝗌𝖾', callback_data="close", style=enums.ButtonStyle.DANGER)]
            ])
        )

    elif query.data == "about":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.ABOUT
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('👨‍💻 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋 👨‍💻', user_id=int(ADMIN))],
                [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start", style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close", style=enums.ButtonStyle.DANGER)]
            ])
        )

    elif query.data == "close":
        await query.message.delete()