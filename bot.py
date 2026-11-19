import os, json, asyncio, threading
try:
    asyncio.set_event_loop(asyncio.new_event_loop())
except: pass
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8880467928
DB_FILE = "groups.json"
AUTO_FILE = "auto.json"
WAITING = set()
AUTO_MSG = {"text": "", "minutes": 15, "on": False}
WA_NUMBER = "250727172400"
WA_LINK = f"https://wa.me/{WA_NUMBER}"

# ========== FLASK - KEEP ALIVE ==========
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive ✅ - RWANDA BUSINESS", 200

@app_flask.route('/health')
def health():
    return "OK", 200

def keep_alive():
    port = int(os.getenv("PORT", 10000))
    threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=port, debug=False, use_reloader=False), daemon=True).start()
# =======================================

def load_groups():
    try:
        with open(DB_FILE) as f: return json.load(f)
    except: return []
def save_groups(g):
    with open(DB_FILE, "w") as f: json.dump(g, f)
def load_auto():
    global AUTO_MSG
    try:
        with open(AUTO_FILE) as f: AUTO_MSG.update(json.load(f))
    except: pass
def save_auto():
    with open(AUTO_FILE, "w") as f: json.dump(AUTO_MSG, f)

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to a Group", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules"),
         InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("📱 Twandikire WhatsApp", url=WA_LINK)],
        [InlineKeyboardButton("✍️ Nyandikira / Support", callback_data="support")],
    ])

def owner_panel():
    groups_count = len(load_groups())
    auto_on = AUTO_MSG.get("on", False)
    auto_min = AUTO_MSG.get("minutes", 15)
    auto_text = AUTO_MSG.get("text", "Nta message washyizeho")[:35]
    status = "ON 🟢" if auto_on else "OFF 🔴"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 OHEREZA HOSE", callback_data="broadcast")],
        [InlineKeyboardButton("▶️ OHEREZA UBU", callback_data="send_now"),
         InlineKeyboardButton("⏰ AUTO 15", callback_data="setauto_help")],
        [InlineKeyboardButton(f"👥 GROUPS: {groups_count}", callback_data="groups"),
         InlineKeyboardButton("👤 USERS", callback_data="users")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats"),
         InlineKeyboardButton("📅 SCHEDULE", callback_data="schedule")],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="premium"),
         InlineKeyboardButton("⚙️ SETTINGS", callback_data="set")],
        [InlineKeyboardButton("📜 RULES", callback_data="rules"),
         InlineKeyboardButton("ℹ️ INFO", callback_data="info")],
        [InlineKeyboardButton("📱 WHATSAPP 0727172400", url=WA_LINK)],
        [InlineKeyboardButton("🆘 HELP", callback_data="help")],
        [InlineKeyboardButton("➕ ADD TO GROUP", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
        [InlineKeyboardButton("✍️ NYANDIKIRA", url="https://t.me/Onlinebu12")],
        [InlineKeyboardButton("🛑 HAGARIKA AUTO", callback_data="stopauto_btn")],
    ]), status, auto_min, auto_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type in ["group", "supergroup"]:
        groups = load_groups()
        if chat.id not in groups:
            groups.append(chat.id); save_groups(groups)
        await update.message.reply_text(
            f"👋 Murakaza neza {user.first_name}!\n\n🇷🇼 Murakaza neza muri {chat.title}!\n\n💰 Hano dufasha kugurisha, kugura no kumenya promotion!\n\n👇 Hitamo:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ ADD TO GROUP", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
                [InlineKeyboardButton("💎 PREMIUM", callback_data="premium")],
                [InlineKeyboardButton("📜 RULES", callback_data="rules"),
                 InlineKeyboardButton("ℹ️ INFO", callback_data="info")],
                [InlineKeyboardButton("📱 Twandikire WhatsApp", url=WA_LINK)],
                [InlineKeyboardButton("✍️ NYANDIKIRA ADMIN", url="https://t.me/Onlinebu12")],
            ])
        )
        return
    if user.id == OWNER_ID:
        kb, status, auto_min, auto_text = owner_panel()
        msg = f"👑 RWANDA BUSINESS PANEL\n\n👥 Groups: {len(load_groups())} | Auto: {status}\n⏰ AUTOMATIC MESSAGE: Buri minota {auto_min}\n📝 {auto_text}\n\nHitamo icyo ushaka:"
        await update.message.reply_text(msg, reply_markup=kb)
        return
    await update.message.reply_text(
        f"👋 Murakaza neza {user.first_name}!\n\n🇷🇼 Murakaza neza kuri RWANDA BUSINESS!\n\n👇 Hitamo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD TO GROUP", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
            [InlineKeyboardButton("💎 PREMIUM", callback_data="premium")],
            [InlineKeyboardButton("📜 RULES", callback_data="rules"),
             InlineKeyboardButton("ℹ️ INFO", callback_data="info")],
            [InlineKeyboardButton("📱 Twandikire WhatsApp - 0727172400", url=WA_LINK)],
            [InlineKeyboardButton("✍️ NYANDIKIRA ADMIN", url="https://t.me/Onlinebu12")],
        ])
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("COMMANDS: /start - Gutangira\n/rules - Amategeko\n/support - Ubufasha", reply_markup=menu())

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    auto_text = f"ON - Buri minota {AUTO_MSG.get('minutes')}" if AUTO_MSG.get("on") else "OFF"
    await update.message.reply_text(f"📊 STATUS\nGroups: {len(load_groups())}\nAuto: {auto_text}\nGroups: {load_groups()}")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta scam.")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ Andika ikibazo cyawe hano, nzagusubiza.")
    WAITING.add(update.effective_user.id)

async def forward_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        groups = load_groups()
        if chat.id not in groups:
            groups.append(chat.id); save_groups(groups)
        return
    if chat.type != "private": return
    user = update.effective_user
    if user.id in WAITING:
        WAITING.remove(user.id)
        await context.bot.send_message(OWNER_ID, f"📩 MESSAGE NSHYA\n👤 {user.first_name} (ID: {user.id})\n\n{update.message.text}")
        await update.message.reply_text("✅ Message yawe yoherejwe. Admin aragusubiza.")

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Andika: /reply ID Ubutumwa"); return
    try:
        await context.bot.send_message(chat_id=int(context.args[0]), text=" ".join(context.args[1:]))
        await update.message.reply_text("✅ Byoherejwe")
    except: await update.message.reply_text("❌ Ntibishoboye koherezwa.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user = q.from_user
    if data == "rules":
        await q.message.reply_text("📜 AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta scam - uzabuzwa burundu.")
        return
    if data == "info":
        await q.message.reply_text(f"🇷🇼 RWANDA BUSINESS\n\nBot izafasha kugurisha, kugura no kumenya promotion!\n\n📱 WhatsApp: 0727172400\nNyandikira: @Onlinebu12")
        return
    if data == "premium":
        await q.message.reply_text("💎 PREMIUM\n\nUshaka Premium? Nyandikira:\n👉 @Onlinebu12\n📱 WhatsApp: 0727172400")
        return
    if data == "support":
        WAITING.add(user.id)
        await q.message.reply_text("✍️ Andika ikibazo cyawe hano, admin aragusubiza.")
        return
    if data == "help":
        await q.message.reply_text("🆘 HELP\n\n/start - Panel\n/rules - Amategeko\n/support - Ubufasha\n\nMuri group andika: /start@Rwanda_onlinebot")
        return
    if user.id != OWNER_ID:
        await q.message.reply_text("❌ Iyi button ni iya Admin gusa.")
        return
    if data == "broadcast":
        await q.message.reply_text("📢 OHEREZA HOSE\n\nAndika:\n/broadcast Ubutumwa bwawe")
    elif data == "send_now":
        if not AUTO_MSG.get("text"):
            await q.message.reply_text("❌ Nta message washyizeho.\nAndika:\n/setauto 15 Ubutumwa bwawe")
        else:
            c = 0
            for gid in load_groups():
                try: await context.bot.send_message(chat_id=gid, text=f"📢 {AUTO_MSG['text']}"); c+=1
                except Exception as e: print(f"Send fail {gid}: {e}")
            await q.message.reply_text(f"✅ OHEREJE UBU muri group {c} ✅")
    elif data == "setauto_help":
        await q.message.reply_text("⏰ AUTO\n\nAndika:\n/setauto 15 Ubutumwa bwawe\n\nKuyihagarika: /stopauto")
    elif data == "stopauto_btn":
        AUTO_MSG["on"] = False; save_auto()
        await q.message.reply_text("🛑 Automatic yahagaritswe.")
    elif data == "groups":
        await q.message.reply_text(f"👥 Ufite Groups: {len(load_groups())}\n\n{load_groups()}")
    elif data == "users":
        await q.message.reply_text("👤 USERS\n\nAbakoresha bageze kuri bot.")
    elif data == "stats":
        await q.message.reply_text(f"📊 STATS\n\n👥 Groups: {len(load_groups())}\n⚡ Auto: {'ON 🟢' if AUTO_MSG.get('on') else 'OFF 🔴'}\n⏰ Minota: {AUTO_MSG.get('minutes')}\n📝 Message: {AUTO_MSG.get('text')[:50]}")
    elif data == "schedule":
        await q.message.reply_text("📅 SCHEDULE\n\n/setauto 15 Ubutumwa bwawe")
    elif data == "set":
        await q.message.reply_text("⚙️ SETTINGS\n\n/setauto 15 Message - Auto\n/stopauto - Hagarika\n/status - Status\n/broadcast Message - Ohereza Hose")
    else:
        await q.message.reply_text("✅ Birakora!")

async def new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    groups = load_groups()
    if chat.id not in groups:
        groups.append(chat.id); save_groups(groups)
    for m in update.message.new_chat_members:
        if m.is_bot: continue
        await update.message.reply_text(f"👋 Murakaza neza {m.first_name}! Andika /start@Rwanda_onlinebot ubone menu.")

async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_id = context.bot.id
    new_members = update.message.new_chat_members
    bot_just_added = any(m.id == bot_id for m in new_members)
    if not bot_just_added:
        return
    chat = update.effective_chat
    if chat.type in ["group", "supergroup", "channel"]:
        groups = load_groups()
        if chat.id not in groups:
            groups.append(chat.id); save_groups(groups)
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"✅ Nemejwe! Nageze muri {chat.title or 'iyi group'}! 🎉\n\nNdi hano, nshobora kwandika nubwo ntaba Admin (muri group).\n\n📱 Twandikire WhatsApp: 0727172400\nAndika /start ubone menu!"
            )
        except Exception as e:
            print(f"Bot added but cannot send in {chat.id}: {e}")
            try:
                await context.bot.send_message(OWNER_ID, f"⚠️ Bot yinjiye muri {chat.title} ({chat.id}) ariko sinashoboye kwandika. Niba ari Channel, nshyiremo Admin.")
            except: pass

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("Andika: /broadcast Murakaza neza"); return
    text = " ".join(context.args); sent = 0
    for gid in load_groups():
        try: await context.bot.send_message(chat_id=gid, text=text); sent+=1
        except: pass
    await update.message.reply_text(f"✅ Byoherejwe muri group {sent} ✅")

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("Andika: /announce Murakaza neza"); return
    text = " ".join(context.args); sent = 0
    for gid in load_groups():
        try: await context.bot.send_message(chat_id=gid, text=f"📢 ITANGAZO\n\n{text}"); sent+=1
        except: pass
    await update.message.reply_text(f"✅ Byoherejwe muri group {sent} ✅")

async def send_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Koresha: /send ID ubutumwa"); return
    try:
        await context.bot.send_message(chat_id=int(context.args[0]), text=" ".join(context.args[1:]))
        await update.message.reply_text("✅ Byoherejwe")
    except: await update.message.reply_text("❌ Ntibishoboye kohereza.")

async def setauto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Koresha: /setauto 15 Murakaza neza"); return
    try: minutes = float(context.args[0])
    except: await update.message.reply_text("Andika umubare w'iminota. Urugero: /setauto 15 ..."); return
    AUTO_MSG.update({"text": " ".join(context.args[1:]), "minutes": minutes, "on": True})
    save_auto()
    await update.message.reply_text(f"✅ AUTOMATIC YEMEJWE! Buri minota {minutes} izajya yohereza:\n{AUTO_MSG['text']}")

async def stopauto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AUTO_MSG["on"] = False; save_auto()
    await update.message.reply_text("🛑 Automatic yahagaritswe.")

async def auto_sender(app):
    while True:
        if AUTO_MSG.get("on") and AUTO_MSG.get("text"):
            for gid in load_groups():
                try: await app.bot.send_message(chat_id=gid, text=f"📢 {AUTO_MSG['text']}")
                except: pass
            await asyncio.sleep(float(AUTO_MSG.get("minutes", 15)) * 60)
        else:
            await asyncio.sleep(30)
async def post_init(app):
    asyncio.create_task(auto_sender(app))

def main():
    keep_alive(); load_auto()
    if not TOKEN:
        print("BOT_TOKEN ntayibonewe"); return
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    async def post_init(app):
    asyncio.create_task(auto_sender(app))

async def run_bot():
    keep_alive(); load_auto()
    if not TOKEN:
        print("BOT_TOKEN ntayibonewe"); return
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CommandHandler("send", send_msg))
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.add_handler(CommandHandler("setauto", setauto))
    app.add_handler(CommandHandler("stopauto", stopauto))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot_added))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_support))
    print("Bot iriruka...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
