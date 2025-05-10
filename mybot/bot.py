import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not BOT_TOKEN or not OWNER_ID:
    raise RuntimeError("请设置 BOT_TOKEN 和 OWNER_ID 环境变量")

user_map = {}

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if message:
        forwarded = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"[来自 {user.first_name} ({user.id}) 的消息]:\n{message.text}"
        )
        user_map[forwarded.message_id] = user.id

async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.reply_to_message:
        reply_to = update.message.reply_to_message
        original_user_id = user_map.get(reply_to.message_id)
        if original_user_id:
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"[来自Bot主人的回复]:\n{update.message.text}"
            )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.User(OWNER_ID)), handle_user_message))
app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), handle_owner_reply))
app.run_polling()
