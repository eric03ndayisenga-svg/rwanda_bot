import os, json, asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8886067024  # ID yawe - ntuyihindure niba ari yo
DB_FILE = "groups.json"
WAITING = set()

# --- Kugirango ikore kuri Render FREE ---
def keep_alive():
    port = int(os.getenv("PORT", 10000))
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"Bot is alive")
        def log_message(self, *a): pass
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), H).serve_forever(), daemon=True).start()

def load_groups():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        return []

def save_groups(g):
    with open(DB_FILE, "w") as f:
        json.dump(g, f)

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to a Group", url="https://t.me/Rwandaonlinebusiness_bot?startgroup=true")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules"), InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("✍️ Nyandikira / Support", callback_data="support")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Murakaza neza kuri Rwanda online business bot wo gucunga amatsinda n'abakiriya bawe. Hitamo:", reply_markup=menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Gutangira\n/rules - Amategeko\n/support - Kuvugana na Admin\n/help - Ubufasha", reply_markup=menu())

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta gutukana")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    WAITING.add(update.effective_user.id)
    await update.message.reply_text("✍️ Andika ikibazo cyawe hano, nzabisubiza vuba.")

async def forward_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    if update.effective_user.id not in WAITING:
        return
    user = update.effective_user
    text = update.message.text
    await context.bot.send_message(OWNER_ID, f"📩 MESSAGE NSHYA\n\nUmutumwa: {user.first_name} (@{user.username})\nID: {user.id}\n\n{text}\n\nKugirango umusubize, andika: /reply {user.id} ubutumwa")
    await update.message.reply_text("Message yawe yoherejwe. Admin azagu...")
    WAITING.remove(update.effective_user.id)

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Andika: /reply ID message")
        return
    target_id = int(context.args[0])
    msg = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=f"💬 Admin: {msg}")
        await update.message.reply_text("Wasubije ✅")
    except:
        await update.message.reply_text("Ntibashije kumwoherereza.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "rules":
        await q.edit_message_text("📜 AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta gutukana", reply_markup=menu())
    elif q.data == "info":
        await q.edit_message_text("Rwanda online business - Bot izanwe na Rwanda online business kugirango ifashe gucunga amatsinda.", reply_markup=menu())
    elif q.data == "support":
        WAITING.add(q.from_user.id)
        await q.edit_message_text("✍️ Andika ikibazo cyawe hano, nzabisubiza vuba.", reply_markup=menu())

async def new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    groups = load_groups()
    if chat.id not in groups:
        groups.append(chat.id)
        save_groups(groups)
    for m in update.message.new_chat_members:
        if m.id == context.bot.id:
            await update.message.reply_text("Murakaza neza! Ndi Rwanda online business bot. Soma /rules")
        else:
            await update.message.reply_text(f"Murakaza neza {m.first_name}! 🇷🇼")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Ni Owner gusa.")
        return
    if not context.args:
        await update.message.reply_text("Andika: /broadcast Murakaza neza")
        return
    text = " ".join(context.args)
    sent = 0
    for gid in load_groups():
        try:
            await context.bot.send_message(chat_id=gid, text=text)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"Yohererejwe muri group {sent} ✅")

async def main():
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", reply))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_support))
    print("Bot iriruka...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
