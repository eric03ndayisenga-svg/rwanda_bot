import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8880467928
DB_FILE = "groups.json"
WAITING = set()

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
        [InlineKeyboardButton("Add me to a Group", url="https://t.me/Rwanda_onlinebot?startgroup=true")],
        [InlineKeyboardButton("Rules", callback_data="rules"), InlineKeyboardButton("Info", callback_data="info")],
        [InlineKeyboardButton("Nyandikira / Support", callback_data="support")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Murakaza neza kuri Rwandaonline business\n\nNdi bot wo gucunga group.\nOngeramo muri group yawe, unyite Admin."
    await update.message.reply_text(msg, reply_markup=menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Menu\n/rules - Amategeko\n/support - Nyandikira\n/broadcast message - Kohereza muri group zose")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AMATEGEKO:\n1. Nta spam\n2. Kubaha abandi\n3. Nta gutukana")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    WAITING.add(update.effective_user.id)
    await update.message.reply_text("Andika ikibazo cyawe hano, nzabwira Admin ako kanya.")

async def forward_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in WAITING:
        return
    user = update.effective_user
    text = "MESSAGE NSHYA\nUmuntu: " + str(user.first_name) + "\nUsername: @" + str(user.username) + "\nID: " + str(uid) + "\nMessage: " + str(update.message.text)
    await context.bot.send_message(chat_id=OWNER_ID, text=text)
    await update.message.reply_text("Message yawe yoherejwe. Admin azagusubiza vuba.")
    WAITING.remove(uid)

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Andika: /reply ID message")
        return
    target_id = int(context.args[0])
    msg = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text="Admin: " + msg)
        await update.message.reply_text("Wasubije.")
    except:
        await update.message.reply_text("Ntabwo nabashije kumwoherereza.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "rules":
        await q.message.reply_text("1. Nta spam\n2. Kubaha abandi\n3. Nta gutukana")
    elif q.data == "info":
        await q.message.reply_text("Rwandaonline business - Bot isanzwe ya group.")
    elif q.data == "support":
        WAITING.add(q.from_user.id)
        await q.message.reply_text("Andika ikibazo cyawe hano, nzabwira Admin.")

async def new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    groups = load_groups()
    if chat.id not in groups:
        groups.append(chat.id)
        save_groups(groups)
    for m in update.message.new_chat_members:
        if m.id == context.bot.id:
            await update.message.reply_text("Murakaza neza! Ndi Rwandaonline bot. Nyite Admin nkore neza.", reply_markup=menu())
        else:
            await update.message.reply_text("Murakaza neza " + str(m.first_name) + "! Soma /rules.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Ni Owner gusa.")
        return
    if not context.args:
        await update.message.reply_text("Andika: /broadcast Murakaza neza")
        return
    text = " ".join(context.args)
    groups = load_groups()
    sent = 0
    for gid in groups:
        try:
            await context.bot.send_message(chat_id=gid, text=text)
            sent += 1
        except:
            pass
    await update.message.reply_text("Yoherejwe muri group " + str(sent) + " / " + str(len(groups)))

import asyncio

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("contact", support))
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
