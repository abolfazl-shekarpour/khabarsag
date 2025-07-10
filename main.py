from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv
from config import source_channels
from utils import clean_text, add_signature
from typing import List, Union, cast

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
admin_id = os.getenv("ADMIN_ID")
target_channel = os.getenv("TARGET_CHANNEL")

if not all([api_id, api_hash, bot_token, admin_id, target_channel]):
    raise ValueError("One or more required environment variables are missing.")

assert api_id is not None and admin_id is not None
api_id = int(api_id)
admin_id = int(admin_id)

# Ensure source_channels is a list of int or str
if not isinstance(source_channels, list):
    source_channels = [source_channels]

app = Client(
    "khabarbaz",
    api_id=api_id,
    api_hash=api_hash,           # type: ignore
    bot_token=bot_token          # type: ignore
)
pending_messages = {}

@app.on_message(filters.channel & filters.chat(cast(List[Union[int, str]], source_channels)))
async def handle_incoming(client, message):
    if not message.text:
        return

    cleaned = clean_text(message.text)
    modified = add_signature(cleaned, target_channel)

    # ذخیره پیام
    pending_messages[message.id] = modified

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ تایید", callback_data=f"accept:{message.id}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject:{message.id}")
    ]])

    await client.send_message(
        admin_id,
        f"📨 *پیش‌نمایش خبر:*\n\n{modified}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    action, msg_id_str = data.split(":")
    msg_id = int(msg_id_str)

    if action == "accept":
        text = pending_messages.get(msg_id)
        if text:
            await client.send_message(target_channel, text)
        await callback_query.message.edit_text("✅ خبر منتشر شد.")
    else:
        await callback_query.message.edit_text("❌ خبر رد شد.")

app.run()
