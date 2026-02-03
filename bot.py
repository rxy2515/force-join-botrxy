import time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8328949950:AAHuiUUoE5oNAcKdzwIhjBZlEljRb67gCFY"    #bot token paste here
CHANNEL = "@popularitytalks"     # Change to your real CHANNEL username
MUTE_SECONDS = 30             # 30 seconds
# ----------------------------------------

# Full permissions for unmuting
FULL_PERMS = ChatPermissions(
    can_send_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_invite_users=True,
)

async def send_force_sub_message(chat_id, user_id, user_name, context):
    """Mute + send subscribe message"""
    until_date = int(time.time()) + MUTE_SECONDS

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
    except:
        pass

    buttons = [
        [InlineKeyboardButton("📢 Subscribe karo Channel", url=f"https://t.me/{CHANNEL.replace('@', '')}")],
        [InlineKeyboardButton("✅ KARLIYA BABU", callback_data=f"checksub:{chat_id}:{user_id}")]
    ]

    text = (
        f"👋 Hi <b>{user_name}</b>!\n\n"
        f"You must join our channel {CHANNEL} to chat here.\n"
        f"You are muted for 30 seconds.\n\n"
        f"After subscribing, click <b>✅ KARLIYA BABU</b>."
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML",
    )


async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new users joining"""
    for user in update.message.new_chat_members:
        if user.is_bot:
            continue
        await send_force_sub_message(
            chat_id=update.effective_chat.id,
            user_id=user.id,
            user_name=user.full_name,
            context=context,
        )


async def message_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check OLD USERS when they send a message"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id

    # Ignore bot messages
    if user.is_bot:
        return

    # Check subscription
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        if member.status not in ("member", "administrator", "creator"):
            # Not subscribed → mute + send message
            await send_force_sub_message(chat_id, user_id, user.full_name, context)
            return
    except:
        return  # Bot not admin in channel

    # Subscribed → allow message (do nothing)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'I SUBSCRIBED' button"""
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    if len(data) != 3:
        return

    _, chat_id, user_id = data
    chat_id = int(chat_id)
    user_id = int(user_id)

    if query.from_user.id != user_id:
        return await query.answer("This is not for you.", show_alert=True)

    # Re-check subscription
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        if member.status in ("member", "administrator", "creator"):
            # Unmute
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=FULL_PERMS,
            )
            await query.edit_message_text("✅ You are subscribed! You are unmuted now.")
        else:
            await query.answer("❗️ You haven't subscribed yet.", show_alert=True)
    except:
        await query.answer("Bot must be admin in channel.", show_alert=True)
        async def start(update, context):
            await update.message.reply_text("Force-subscribe bot active!")


def main():
    from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update, context):
    await update.message.reply_text("Force-subscribe bot active!")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if name == "__main__":
    main()
