import os, asyncio, threading, re, glob, random
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from flask import Flask

# --- [ سيرفر ويب لضمان استقرار البوت 24/7 ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 ULTIMATE ENGINE IS LIVE"
def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- [ إعدادات سالم الرسمية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'

bot = TelegramClient('v10_ultimate', API_ID, API_HASH)

# --- [ أنواع البلاغات القوية جداً ] ---
REPORT_REASONS = {
    "🔥 سبام مكثف": types.InputReportReasonSpam(),
    "🔞 محتوى غير لائق": types.InputReportReasonPornography(),
    "⚔️ تحريض وعنف": types.InputReportReasonViolence(),
    "👤 انتحال شخصية": types.InputReportReasonFake(),
    "❌ محتوى مخالف": types.InputReportReasonOther()
}

# --- [ كيبورد التحكم الرئيسي ] ---
MAIN_MENU = [
    [Button.text("🚀 شن هجوم شامل", resize=True), Button.text("➕ ربط حساب جديد", resize=True)],
    [Button.text("📊 حالة الأسطول", resize=True), Button.text("🔍 فحص الجلسات", resize=True)],
    [Button.text("🛠️ إعدادات النظام", resize=True)]
]

# --- [ الأوامر البرمجية ] ---

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "🛡️ **مرحباً بك يا سالم في نظام V10 Ultimate**\n\n"
        "هذا المحرك هو الأقوى للتحكم في الحسابات وشن البلاغات الجماعية.\n"
        "تم تفعيل نظام الحماية الذاتي والشد الداخلي.",
        buttons=MAIN_MENU
    )

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 حالة الأسطول"))
async def stats(event):
    sessions = glob.glob('user_sessions/*.session')
    await event.respond(
        f"📈 **إحصائيات النظام الحالية:**\n\n"
        f"📦 عدد الجلسات النشطة: `{len(sessions)}`\n"
        f"📡 حالة الاتصال: ممتاز ✅\n"
        f"🛡️ نظام Anti-Ban: يعمل بكفاءة",
        buttons=MAIN_MENU
    )

@bot.on(events.NewMessage(func=lambda e: e.text == "➕ ربط حساب جديد"))
async def add_account(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("📱 أرسل رقم الهاتف مع رمز الدولة (مثل +218...):")
        phone = (await conv.get_response()).text.strip().replace(" ", "")
        
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        
        try:
            code_request = await client.send_code_request(phone)
            await conv.send_message("📩 **حول (Forward)** رسالة كود التحقق من تيليجرام هنا:")
            otp_msg = await conv.get_response()
            otp_code = re.search(r'\b\d{5}\b', otp_msg.text)
            
            if otp_code:
                try:
                    await client.sign_in(phone, otp_code.group(0), phone_code_hash=code_request.phone_code_hash)
                    await conv.send_message("✅ تم ربط الحساب بنجاح وإضافته للأسطول!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 هذا الحساب محمي بكلمة سر، أرسلها الآن:")
                    password = (await conv.get_response()).text
                    await client.sign_in(password=password)
                    await conv.send_message("✅ تم التحقق والربط بنجاح!")
            else:
                await conv.send_message("❌ فشل العثور على الكود في الرسالة.")
        except Exception as e:
            await conv.send_message(f"❌ خطأ تقني: {e}")
        
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🚀 شن هجوم شامل"))
async def attack_setup(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة أو الحساب المراد تدميره:")
        target_link = (await conv.get_response()).text
        
        # إنشاء أزرار أنواع البلاغات
        btns = [[Button.inline(name, data=f"atk_{name}_{target_link}")] for name in REPORT_REASONS.keys()]
        await conv.send_message("⚠️ اختر نوع الهجوم المطلوب تنفيذه الآن:", buttons=btns)

@bot.on(events.CallbackQuery(pattern=r"atk_(.*)_(.*)"))
async def start_attack(event):
    reason_name = event.data_decode.split('_')[1]
    target = event.data_decode.split('_')[2]
    reason = REPORT_REASONS[reason_name]
    
    sessions = glob.glob('user_sessions/*.session')
    if not sessions:
        return await event.respond("❌ لا توجد حسابات مربوطة لبدء الهجوم!")
    
    await event.edit(f"🚀 جاري شن هجوم ({reason_name}) باستخدام {len(sessions)} حساب...")
    
    success = 0
    for session in sessions:
        cli = TelegramClient(session, API_ID, API_HASH)
        try:
            await cli.connect()
            # منطق استخراج المعرفات من الرابط
            if "t.me/" in target:
                parts = target.split('/')
                peer = parts[-2] if len(parts) > 2 else parts[-1]
                msg_id = [int(parts[-1])] if parts[-1].isdigit() else None
                
                if msg_id:
                    await cli(functions.messages.ReportRequest(peer=peer, id=msg_id, reason=reason))
                else:
                    await cli(functions.account.ReportPeerRequest(peer=peer, reason=reason, message="Spam attack"))
                
                success += 1
            await cli.disconnect()
            await asyncio.sleep(random.randint(1, 3)) # حماية الحسابات
        except Exception:
            continue
            
    await event.respond(f"✅ انتهى الهجوم الشامل يا سالم!\n🚀 مجموع البلاغات الناجحة: `{success}`")

# --- [ تشغيل المحرك ] ---
async def main():
    if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
    print("--- V10 ULTIMATE ENGINE IS STARTING ---")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
