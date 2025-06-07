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
✨ **GET CONTACT TARZI ÇALIŞAN BİR BOTUM** ✨

ℹ️ **BİLGİLER**

▸ **Kullanıcılar:** {total_users}
▸ **Etiket:** {len(user_friends.get(user.id, []))}

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
        await message.reply("❌ Kullanım:\n\n /add 905449090000 CERENIM")
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
            await message.reply(f"✅ BAŞARILI:\n\nNumara: {number}\nEtiket: {tag}")
        else:
            await message.reply("❌ Etiket Eklenirken Bir Hata Oluştu.")
    except Exception as e:
        logger.error(f"Add tag error: {e}")
        await message.reply("❌ API Bağlantı Hatası.")



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
        
        # API yanıtını loglayalım
        logger.info(f"API Response for {number}: {response.text}")
        
        if response.status_code == 200:
            # Ham veriyi analiz edelim
            if not response.text.strip():
                await loading_msg.edit("❌ API boş yanıt verdi")
                return
                
            # Veriyi işleme
            tags = []
            try:
                # JSON formatında mı kontrol edelim
                data = response.json()
                if isinstance(data, list):
                    tags = data
                elif isinstance(data, dict):
                    tags = [data]
            except ValueError:
                # JSON değilse, metin olarak işle
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.startswith('"phone":'):
                        phone = line.split('"phone":')[1].strip(' ,')
                        tags.append({"phone": phone})
                    elif line.startswith('"label":'):
                        if tags:
                            tags[-1]["label"] = line.split('"label":')[1].strip(' ,')
                    elif line.startswith('"created_by":'):
                        if tags:
                            tags[-1]["created_by"] = line.split('"created_by":')[1].strip(' ,')
                    elif line.startswith('"created_at":'):
                        if tags:
                            tags[-1]["created_at"] = line.split('"created_at":')[1].strip(' ,')
            
            # Filtreleme
            filtered_tags = [tag for tag in tags if str(tag.get("phone")) == str(number)]
            
            if filtered_tags:
                # Dosyaya yaz
                with open("tag.txt", "w", encoding="utf-8") as f:
                    f.write(f"📱 {number} NUMARASINA AİT ETİKETLER\n\n")
                    for tag in filtered_tags:
                        f.write(f"• ETİKET: {tag.get('label', 'N/A')}\n")
                        f.write(f"  EKLEYEN: {tag.get('created_by', 'N/A')}\n")
                        f.write(f"  TARİH: {tag.get('created_at', 'N/A')}\n\n")
                
                # Kullanıcıya gönder
                await loading_msg.delete()
                await message.reply_document(
                    document="tag.txt",
                    caption=f"✅ {len(filtered_tags)} adet etiket bulundu",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔍 Yeni Arama", callback_data="fetch_tags")]
                    ])
                )
            else:
                await loading_msg.edit(f"❌ {number} Etiket Bulunamadı\n\nAPI Yanıtı:\n{response.text[:300]}...")
        else:
            await loading_msg.edit(f"🔴 API hatası! HTTP {response.status_code}\n\n{response.text[:300]}...")

    except Exception as e:
        error_msg = f"⛔ Hata: {str(e)}"
        logger.error(f"API Error for {number}: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}")
        await loading_msg.edit(error_msg)
                    
            
    
                                              
@app.on_message(filters.command("list"))
async def list_tags_command(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_friends or not user_friends[user_id]:
        await message.reply("ℹ️ BİLGİ\n\nHenüz Hiç Etiket Eklemediniz.")
        return
    
    tag_list = "\n".join([f"📌 {item['number']} - {item['tag']}" for item in user_friends[user_id]])
    await message.reply(f"📋 BİLGİ\n\nEtiket Listeniz:\n\n{tag_list}")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user = query.from_user
    data = query.data
    
    if data == "help":
        await query.edit_message_text(
            "📚 **Yardım Menüsü**\n\n"                  
            "• /add = Etiketi Ekler\n"
            "• /hashtag = Ettiketleri Listeler\n"
            "• /list = Listeler\n\n"
            "ÖRNEK:\n\n"
            "/add 905449090000 CERENIM\n"
            "/hashtag 905449090000\n\n",
            reply_markup=HELP_BUTTONS
        )
    
    elif data == "add_tag":
        await query.answer("İSTERSEN YARDIM KLAVUZU OKU", show_alert=True)
    
    elif data == "fetch_tags":
        await query.answer("kullanım: /hashtag", show_alert=True)
    
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
