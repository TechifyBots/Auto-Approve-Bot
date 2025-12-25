import traceback
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import *
from pyrogram.errors import ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
from config import *
from .db import tb

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_id = message.from_user.id
    session = await tb.get_session(user_id)
    if session is None:
        return
    await tb.set_session(user_id, session=None)
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_id = message.from_user.id
    session = await tb.get_session(user_id)
    if session is not None:
        await message.reply("**You are already logged in. Please /logout first before logging in again.**")
        return
    phone_number_msg = await bot.ask(
        chat_id=user_id,
        text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>"
    )
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    await phone_number_msg.reply("Sending OTP...")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(
            user_id,
            "Check your official Telegram account for OTP. If you got it, send it here as shown:\n\nIf OTP is `12345`, **send as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel.**",
            filters=filters.text,
            timeout=600
        )
    except PhoneNumberInvalid:
        return await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
    if phone_code_msg.text == '/cancel':
        return await phone_code_msg.reply('<b>Process cancelled!</b>')
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        return await phone_code_msg.reply('**OTP is invalid.**')
    except PhoneCodeExpired:
        return await phone_code_msg.reply('**OTP is expired.**')
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(
            user_id,
            '**Two-step verification is enabled. Please send your password.**\n\n**Enter /cancel to cancel.**',
            filters=filters.text,
            timeout=300
        )
        if two_step_msg.text == '/cancel':
            return await two_step_msg.reply('<b>Process cancelled!</b>')
        try:
            await client.check_password(password=two_step_msg.text)
        except PasswordHashInvalid:
            return await two_step_msg.reply('**Invalid password provided.**')
    string_session = await client.export_session_string()
    await client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string</b>')
    try:
        await tb.set_session(user_id, string_session)
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
    await bot.send_message(
        user_id,
        "<b>Account logged in successfully.\n\nIf you get any AUTH KEY related error, use /logout and /login again.</b>"
    )
