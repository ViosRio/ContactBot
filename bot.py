#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
import requests
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

# API Endpoints
TAG_ADD_API = "https://cerenviosvipx.serv00.net/pages/add_tag.php"
TAG_FETCH_API = "https://cerenviosvipx.serv00.net/pages/data.php"

# Başlangıç Mesajı
def get_start_message(user):
    global total_users
    emoji = choice(["🔥", "❤️", "🌹", "🎯"])
    return f"""
✨ **GET CONTACT - Numara Etiket Botu** ✨
👥 **Toplam Kullanıcılar:** {total_users}

▸ **Çekilen Sorgu:** {hastag_status.get(user.id, "Yok")}
▸ **Etiket Sayısı:** {len(user_friends.get(user.id, []))}

{emoji} Powered by DeepSeek ❤️‍🔥
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📜 Yardım", callback_data="help"),
        InlineKeyboardButton("⚙️ Api", url=f"https://cerenviosvipx.serv00.net/")
    ],
    [
        InlineKeyboardButton("👤 Kurucu", url=f"https://t.me/{OWNER_USERNAME}")
    ],
])

TAG_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Etiket Ekle", callback_data="add_tag")],
    [InlineKeyboardButton("🔍 Etiket Çek", callback_data="fetch_tags")],
    [InlineKeyboardButton("📋 Etiket Listem", callback_data="list_tags")],
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
async def add_tag_command(client, message):
    if len(message.command) < 3:
        await message.reply("❌ Kullanım: /add <numara> <etiket>\nÖrnek: /add 905449090000 CERENIM")
        return
    
    number = message.command[1]
    tag = " ".join(message.command[2:])
    
    try:
        # API'ye istek gönder
        response = requests.get(f"{TAG_ADD_API}?phone={number}&tag={tag}")
        
        if response.status_code == 200:
            # Kullanıcının etiket listesine ekle
            if message.from_user.id not in user_friends:
                user_friends[message.from_user.id] = []
            
            user_friends[message.from_user.id].append({"number": number, "tag": tag})
            await message.reply(f"✅ Başarıyla etiket eklendi:\n\nNumara: {number}\nEtiket: {tag}")
        else:
            await message.reply("❌ Etiket eklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
    except Exception as e:
        logger.error(f"Add tag error: {e}")
        await message.reply("❌ API bağlantı hatası. Lütfen daha sonra tekrar deneyin.")



async def fetch_tags_from_api(number: str) -> list:
    """Improved tag fetching function with better error handling"""
    try:
        response = requests.get(f"{TAG_FETCH_API}?gsm={number}", timeout=10)
        
        if response.status_code == 200:
            # Try different parsing methods based on response format
            try:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data] if data.get("phone") else []
            except ValueError:
                # If not JSON, try to parse as text
                content = response.text.strip()
                if content:
                    return [{"label": content, "phone": number}]
                
        return []
    except Exception as e:
        logger.error(f"API fetch error for {number}: {str(e)}")
        return []

@app.on_message(filters.command("hashtag"))
async def fetch_tags_command(client, message):
    if len(message.command) < 2:
        await message.reply("❌ KULLANIM:\n\n /hashtag 905449090000")
        return
    
    number = message.command[1]
    loading_msg = await message.reply("⏳ Lütfen Bekleyin...")

    try:
        response = requests.get(f"https://cerenviosvipx.serv00.net/pages/data.php?gsm={number}")
        
        if response.status_code == 200:
            # Tüm API verilerini işle
            all_tags = []
            current_tag = {}
            
            for line in response.text.split('\n'):
                line = line.strip()
                if '"phone":' in line:
                    current_tag["phone"] = line.split('"phone":')[1].strip('", ')
                elif '"label":' in line:
                    current_tag["label"] = line.split('"label":')[1].strip('", ')
                elif '"created_by":' in line:
                    current_tag["created_by"] = line.split('"created_by":')[1].strip('", ')
                elif '"created_at":' in line:
                    current_tag["created_at"] = line.split('"created_at":')[1].strip('", ')
                    if current_tag.get("phone") == number:
                        all_tags.append(current_tag)
                    current_tag = {}
            
            if all_tags:
                # Tüm sonuçları dosyaya yaz
                with open("tag.txt", "w", encoding="utf-8") as f:
                    f.write(f"📱 {number} NUMARASINA AİT TÜM ETİKETLER ({len(all_tags)} adet)\n\n")
                    for tag in all_tags:
                        f.write(f"• Etiket: {tag.get('label', 'N/A')}\n")
                        f.write(f"  Ekleyen: {tag.get('created_by', 'N/A')}\n")
                        f.write(f"  Tarih: {tag.get('created_at', 'N/A')}\n\n")
                
                # Dosyayı gönder
                await loading_msg.delete()
                await message.reply_document(
                    document="tag.txt",
                    caption=f"✅ BAŞARILI",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔍 Yeni Arama", callback_data="fetch_tags")]
                    ])
                )
            else:
                await loading_msg.edit(f"❌ {number} numarasına ait etiket bulunamadı")
        else:
            await loading_msg.edit("🔴 API hatası! Lütfen daha sonra tekrar dene")

    except Exception as e:
        await loading_msg.edit(f"⛔ Hata: {str(e)}")
        logger.error(f"API Error: {e}")
    
                
                
        
        

@app.on_message(filters.command("list"))
async def list_tags_command(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_friends or not user_friends[user_id]:
        await message.reply("ℹ️ Henüz hiç etiket eklemediniz.")
        return
    
    tag_list = "\n".join([f"📌 {item['number']} - {item['tag']}" for item in user_friends[user_id]])
    await message.reply(f"📋 **Etiket Listeniz:**\n\n{tag_list}")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user = query.from_user
    data = query.data
    
    if data == "help":
        await query.edit_message_text(
            "📚 **Yardım Menüsü**\n\n"                  
            "• /add <numara> <etiket> - Numara etiketi ekler\n"
            "• /hashtag <numara> - Numaraya ait etiketleri çeker\n"
            "• /list - Eklediğiniz etiketleri listeler\n"
            "• /settings - Ayarlar\n\n"
            "Örnek Kullanımlar:\n"
            "/add 905449090000 CERENIM\n"
            "/hashtag 905449090000\n\n",
            reply_markup=HELP_BUTTONS
        )
    
    elif data == "add_tag":
        await query.answer("Lütfen şu şekilde komut kullanın: /add <numara> <etiket>", show_alert=True)
    
    elif data == "fetch_tags":
        await query.answer("Lütfen şu şekilde komut kullanın: /hashtag <numara>", show_alert=True)
    
    elif data == "list_tags":
        await list_tags_command(client, query.message)
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)

# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
