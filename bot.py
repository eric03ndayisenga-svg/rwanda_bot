import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8880467928
DB_FILE = "groups.json"

def load_groups():
    try:
        with open(DB_FILE) as f: return json.load(f)
    except: return []
def save_groups(g):
    with open(DB_FILE, "w") as f: json.dump(g, f)

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add me to a Group", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
        [InlineKeyboardButton("📜 Rules", callback_data="rules"), InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("🚨 Nyandikira / Support", callback_data="support")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Murakaza neza kuri *Rwandaonline business*\n\n"
        "Ndi bot wo gucunga group.\n"
        "Ongeramo muri group yawe, unyite Admin.\n"
        "Niba unkeneye, kanda 🚨 Nyandikira.",
        parse_mode="Markdown", reply_markup=menu()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 COMMANDS:\n"
        "/start - Menu\n"
        "/rules - Amategeko\n"
        "/support - Nyandikira\n"
        "/broadcast message - Kohereza muri group zose (Wowe gusa)"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta gutukana\n4. Kurikiza amabwiriza ya Admin")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 Andika ikibazo cyawe / icyo unkeneye hano, nzabwira Admin ako kanya.")
    context.user_data["waiting_support"] = True

async def forward_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_support"):
        return
    user = update.effective_user
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📩 MESSAGE NSHYA\n\nUmuntu: {user.first_name}\nUsername: @{user.username}\nID: {user.id}\n\nMessage: {update.message.text}\n\nGusubiza: /reply {user.id} message yawe",
    )
    await update.message.reply_text("✅ Message yawe yoherejwe. Admin azagusubiza vuba.")
    context.user_data.pop("waiting_support", None)

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Andika: /reply ID message")
        return
    target_id = int(context.args[0])
    msg = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=f"💬 Admin: \n\n{msg}")
        await update.message.reply_text("✅ Wasubije.")
    except:
        await update.message.reply_text("❌ Ntabwo nabashije kumwoherereza.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "rules":
        await q.message.reply_text("📜 1. Nta
