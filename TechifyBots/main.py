import traceback
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
from config import API_ID, API_HASH
from .database import tb

SESSION_STRING_SIZE = 351

@Client.on_message(filters.command("login") & filters.private)
async def main(client, message):
    user_id = message.from_user.id
    session = await tb.get_session(user_id)
    if session is not None:
        await message.reply("**You are already logged in. Please /logout first before logging in again.**")
        return
    await message.reply("<b>Please send your phone number which includes country code</b>\n<b>Example:</b>\n<code>+13124562345, +9171828181889</code>")
    phone_number_msg = await client.listen(message.chat.id, timeout=None)
    if not phone_number_msg.text:
        return
    if phone_number_msg.text.startswith('/'):
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    phone_number = phone_number_msg.text.strip()
    user_client = Client(":memory:", API_ID, API_HASH)
    await user_client.connect()
    try:
        code = await user_client.send_code(phone_number)
    except PhoneNumberInvalid:
        await user_client.disconnect()
        return await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
    await phone_number_msg.reply("Check your official Telegram account for OTP. If you got it, send it here as shown:\n\nIf OTP is `12345`, **send as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel.**")
    while True:
        phone_code_msg = await client.listen(message.chat.id, timeout=None)
        if not phone_code_msg.text:
            continue
        if phone_code_msg.text.startswith('/'):
            await user_client.disconnect()
            return await phone_code_msg.reply('<b>Process cancelled!</b>')
        phone_code = phone_code_msg.text.strip()
        if not re.fullmatch(r"\d \d \d \d \d", phone_code):
            await phone_code_msg.reply("**OTP is invalid.**\n\nPlease send the OTP in this format:\n`1 2 3 4 5`")
            continue
        phone_code = phone_code.replace(" ", "")
        try:
            await user_client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except PhoneCodeInvalid:
            return await phone_code_msg.reply('**OTP is invalid.**')
        except PhoneCodeExpired:
            await user_client.disconnect()
            return await phone_code_msg.reply('**OTP is expired.**')
        except SessionPasswordNeeded:
            await phone_code_msg.reply('**Two-step verification is enabled. Please send your password.**\n\n**Enter /cancel to cancel.**')
            two_step_msg = await client.listen(message.chat.id, timeout=None)
            if not two_step_msg.text:
                continue
            if two_step_msg.text.startswith('/'):
                await user_client.disconnect()
                return await two_step_msg.reply('<b>Process cancelled!</b>')
            try:
                await user_client.check_password(password=two_step_msg.text)
            except PasswordHashInvalid:
                await user_client.disconnect()
                return await two_step_msg.reply('**Invalid password provided.**')
        break
    string_session = await user_client.export_session_string()
    await user_client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string</b>')
    try:
        await tb.set_session(user_id, string_session)
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
    await client.send_message(user_id, "<b>Account logged in successfully.\n\nIf you get any AUTH KEY related error, use /logout and /login again.</b>")

@Client.on_message(filters.command("logout") & filters.private)
async def logout(client, message):
    user_id = message.from_user.id
    session = await tb.get_session(user_id)
    if session is None:
        return await message.reply("**You haven't logged in yet. Why are you trying to log out? 😅**")
    await tb.set_session(user_id, session=None)
    await message.reply("**Logout Successfully** ♦")