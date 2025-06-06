#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
from pathlib import Path
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import asyncio
from random import choice
import logging
from config import *

# 1. CLIENT TANIMI (EN ÜSTTE)
app = Client(
    "roxy-mask",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Veritabanı klasörü
DATA_DIR = Path("data")
LIST_DIR = DATA_DIR / "list"
LIST_DIR.mkdir(parents=True, exist_ok=True)

# Global değişkenler
active_chats = {}
waiting_users = {}
hastag_status = {}
private_mode = {}
user_friends = {}  # Arkadaş listesi için
total_users = 0    # Toplam kullanıcı sayısı

# Başlangıç Mesajı
def get_start_message(user):
    global total_users
    emoji = choice(["🔥", "❤️", "🌹", "🎯"])
    return f"""
✨ **GET CONTACT - Numara Etiket Botu** ✨
👥 **Toplam Kullanıcılar:** {total_users}

▸ **Çekilen Sorgu:** {hastag_status}
▸ **Etiket Sayısı:** {len(user_friends.get(user.id, []))}

 Powered by DeepSeek ❤️‍🔥
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📜 Yardım", callback_data="help"),
        InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings")
    ],
    [
        InlineKeyboardButton("👤 Kurucu", url=f"https://t.me/{OWNER_USERNAME}")
    ],
])

FRIENDS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Etiket Ekle", callback_data="add_friend")],
    [InlineKeyboardButton("📋 Etiket Listesi", callback_data="list_friends")],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

HELP_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔍 Komutlar", callback_data="commands"),
        InlineKeyboardButton("💡 Nasıl Kullanılır?", callback_data="how_to_use")
    ],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

# Handler'lar
@app.on_message(filters.command("start"))
async def start(client, message):
    global total_users
    user = message.from_user
    if user.id not in user_friends:
        user_friends[user.id] = []
        total_users += 1
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(user),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.command("add"))
async def add_friend(client, message):
    if len(message.command) > 1:
        friend_id = message.command[1]
        if message.from_user.id not in user_friends:
            user_friends[message.from_user.id] = []
        if friend_id not in user_friends[message.from_user.id]:
            user_friends[message.from_user.id].append(friend_id)
            await message.reply(f"✅ : BAŞARIYLA ETİKET EKLENDİ {number}")
        else:
    else:
        await message.reply("• Kullanım ✅:\n\n /add 905449090000 CERENİM")


# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user = query.from_user
    data = query.data
    
    if data == "find_partner":
        if user.id in active_chats:
            await query.answer("Zaten bir sohbettesiniz!", show_alert=True)
            return
        
        # Eşleşme işlemi              
    elif data == "help":
        await query.edit_message_text(
            "📚 **Yardım Menüsü**\n\n"                  
            "• /add CEREN = Etiket Ekle\n"
            "• /hashtag = Etiket Çek\n"
            "• /settings = Ayarlar\n\n"
            reply_markup=HELP_BUTTONS
        )
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)

def is_not_command(_, __, m: Message):
    return not m.text.startswith('/')


# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
