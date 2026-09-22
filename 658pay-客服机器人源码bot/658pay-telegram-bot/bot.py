"""658pay Telegram customer-support relay bot (long polling)."""
from __future__ import annotations

import asyncio
from html import escape
import logging
import os
from typing import Final

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from database import Database

LOG = logging.getLogger(__name__)
BOT_TOKEN: Final[str] = os.environ.get("BOT_TOKEN", "")
ADMIN_ID_TEXT: Final[str] = os.environ.get("ADMIN_ID", "")
DATABASE_PATH: Final[str] = os.environ.get("DATABASE_PATH", "/app/data/658pay.db")

FAQ = {
    "about": ("About 658pay", "658pay provides payment services designed to offer a secure, stable, and efficient payment experience.\n\nPlease review the requirements and conditions of each task before proceeding."),
    "earn": ("How To Earn", "1. Download the 658pay app\n2. Register your account\n3. Add supported UPI and wallet methods\n4. Check available tasks\n5. Complete tasks according to their instructions\n6. Receive eligible task rewards under the platform rules\n\nYou may also become an Agent and earn eligible commission from your team."),
    "deposit_menu": ("Deposit Issues", "Choose an issue below:"),
    "withdraw_menu": ("Withdrawal Issues", "Choose an issue below:"),
    "agent_menu": ("Agent Commission", "Choose an item below:"),
    "contact": ("Contact Support", "Send your question, screenshot, receipt, image, video, or file directly to this bot. Include your User ID or order number for a specific transaction.\n\nYour message will be forwarded to 658pay support. Please never send passwords or OTP codes."),
    "dep_new": ("No New Orders", "Available orders may already have been claimed. Please wait for the system to release new orders and check again later."),
    "dep_occupied": ("Order Is Occupied", "This order has already been claimed by another member. Please try another available order when one is released."),
    "dep_pending": ("Deposit Pending", "Please allow time for the bank or payment provider to process the transaction. If it remains pending unusually long, contact support with the order information."),
    "dep_failed": ("Deposit Order Failed", "Deposit orders have a time limit. If payment or confirmation was not completed in time, the order may not be credited automatically. Contact support with the order details and receipt for review."),
    "with_none": ("No Withdrawal Orders / Can't Withdraw", "Make sure your supported UPI payment methods are enabled, then wait for the system to match an available withdrawal order. Processing time depends on availability."),
    "with_pending": ("Pending Withdrawal Order", "If an amount is temporarily locked by an active order, wait for its status to update. If the status remains unchanged, contact support."),
    "with_failed": ("Receive Order Failed", "If a receive order fails, the corresponding amount is normally returned according to platform processing rules. The system may match another order afterward; contact support if the status remains abnormal."),
    "agent_how": ("How to Become an Agent", "Open Home → Team → Invitation Link. Share your personal link. When invited users complete eligible tasks, you may receive commission according to the platform rules."),
    "agent_rate": ("Agent Commission Rates", "Level 1 Agent Commission: 0.5%\nLevel 2 Agent Commission: 0.1%\n\nRates apply to eligible completed task amounts under the platform rules. Contact your online manager for guidance."),
}


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 About 658pay", callback_data="about"), InlineKeyboardButton("💰 How To Earn", callback_data="earn")],
        [InlineKeyboardButton("💳 Deposit Issues", callback_data="deposit_menu"), InlineKeyboardButton("💸 Withdrawal Issues", callback_data="withdraw_menu")],
        [InlineKeyboardButton("👥 Agent Commission", callback_data="agent_menu"), InlineKeyboardButton("💬 Contact Support", callback_data="contact")],
    ])


def submenu(key: str) -> InlineKeyboardMarkup | None:
    choices = {
        "deposit_menu": [("No New Orders", "dep_new"), ("Order Occupied", "dep_occupied"), ("Deposit Pending", "dep_pending"), ("Deposit Failed", "dep_failed")],
        "withdraw_menu": [("No Withdrawal Orders", "with_none"), ("Pending Withdrawal", "with_pending"), ("Receive Order Failed", "with_failed")],
        "agent_menu": [("How to Become an Agent", "agent_how"), ("Commission Rates", "agent_rate")],
    }.get(key)
    if not choices:
        return None
    rows = [[InlineKeyboardButton(label, callback_data=value)] for label, value in choices]
    rows.append([InlineKeyboardButton("← Main Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def is_admin(update: Update, admin_id: int) -> bool:
    return bool(update.effective_user and update.effective_user.id == admin_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.message:
        return
    db: Database = context.application.bot_data["db"]
    db.upsert_customer(user.id, user.username, user.full_name)
    await update.message.reply_text("Welcome to 658pay Customer Support. Choose a topic below, or send a message directly to our support team.", reply_markup=main_keyboard())


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    key = query.data
    if key == "menu":
        await query.message.edit_text("658pay Customer Support\n\nChoose a topic below, or send a message directly to our support team.", reply_markup=main_keyboard())
        return
    title, text = FAQ.get(key, ("Help", "Please choose an option from the menu."))
    await query.message.edit_text(f"<b>{title}</b>\n\n{text}", parse_mode=ParseMode.HTML, reply_markup=submenu(key) or InlineKeyboardMarkup([[InlineKeyboardButton("← Main Menu", callback_data="menu")]]))


async def relay_customer_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user
    if not message or not user:
        return
    admin_id: int = context.application.bot_data["admin_id"]
    db: Database = context.application.bot_data["db"]
    db.upsert_customer(user.id, user.username, user.full_name)
    if db.is_blocked(user.id):
        await message.reply_text("Support is currently unavailable for this account.")
        return
    username = f"@{user.username}" if user.username else "(not set)"
    header = await context.bot.send_message(admin_id, f"👤 <b>Customer message</b>\nName: {escape(user.full_name)}\nUsername: {escape(username)}\nUser ID: <code>{user.id}</code>\n\nReply directly to this message or the copied message below to reply to the customer.", parse_mode=ParseMode.HTML)
    db.map_admin_message(admin_id, header.message_id, user.id)
    try:
        copied = await context.bot.copy_message(chat_id=admin_id, from_chat_id=message.chat_id, message_id=message.message_id)
        db.map_admin_message(admin_id, copied.message_id, user.id)
    except TelegramError:
        LOG.exception("Could not copy customer message for customer_id=%s", user.id)
        await context.bot.send_message(admin_id, "⚠️ The customer message could not be copied. Please ask the customer to resend it.")
    await message.reply_text("✅ Your message has been received. Our support team will reply through this bot as soon as possible.")


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.reply_to_message:
        return
    admin_id: int = context.application.bot_data["admin_id"]
    db: Database = context.application.bot_data["db"]
    customer_id = db.customer_for_admin_message(admin_id, message.reply_to_message.message_id)
    if not customer_id:
        return
    try:
        await context.bot.copy_message(chat_id=customer_id, from_chat_id=message.chat_id, message_id=message.message_id)
        await message.reply_text("✅ Sent to customer.")
    except Forbidden:
        await message.reply_text("⚠️ Delivery failed: this customer has blocked the bot or has not started it.")
    except TelegramError:
        LOG.exception("Could not relay admin reply to customer_id=%s", customer_id)
        await message.reply_text("⚠️ Delivery failed. Please try again later.")


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update, context.application.bot_data["admin_id"]):
        return
    db: Database = context.application.bot_data["db"]
    await update.message.reply_text(f"Registered customers: {db.user_count()}")


async def set_block(update: Update, context: ContextTypes.DEFAULT_TYPE, blocked: bool) -> None:
    if not is_admin(update, context.application.bot_data["admin_id"]):
        return
    if not context.args or not context.args[0].lstrip("-").isdigit():
        await update.message.reply_text("Usage: /block <telegram_id>" if blocked else "Usage: /unblock <telegram_id>")
        return
    customer_id = int(context.args[0])
    db: Database = context.application.bot_data["db"]
    if db.set_blocked(customer_id, blocked):
        await update.message.reply_text(f"Customer {customer_id} is now {'blocked' if blocked else 'unblocked'}.")
    else:
        await update.message.reply_text("Customer ID not found.")


async def block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_block(update, context, True)


async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_block(update, context, False)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update, context.application.bot_data["admin_id"]):
        return
    message = update.message
    if not message:
        return
    text = " ".join(context.args).strip()
    source = message.reply_to_message
    if not text and not source:
        await message.reply_text("Usage: /broadcast <text>\nOr reply to a media message with /broadcast [optional caption].")
        return
    db: Database = context.application.bot_data["db"]
    sent = failed = 0
    for customer_id in db.broadcast_recipients():
        try:
            if source:
                await context.bot.copy_message(chat_id=customer_id, from_chat_id=message.chat_id, message_id=source.message_id, caption=text or None)
            else:
                await context.bot.send_message(customer_id, text)
            sent += 1
            await asyncio.sleep(0.04)
        except (Forbidden, BadRequest):
            failed += 1
        except TelegramError:
            failed += 1
            LOG.exception("Broadcast failed for customer_id=%s", customer_id)
    await message.reply_text(f"Broadcast complete. Sent: {sent}; failed: {failed}.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOG.exception("Unhandled exception while processing update %r", update, exc_info=context.error)


def main() -> None:
    if not BOT_TOKEN or not ADMIN_ID_TEXT:
        raise RuntimeError("BOT_TOKEN and ADMIN_ID environment variables are required.")
    try:
        admin_id = int(ADMIN_ID_TEXT)
    except ValueError as exc:
        raise RuntimeError("ADMIN_ID must be a Telegram numeric user ID.") from exc
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data["admin_id"] = admin_id
    app.bot_data["db"] = Database(DATABASE_PATH)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("unblock", unblock))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(faq_callback))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.User(user_id=admin_id) & ~filters.COMMAND, admin_reply))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.User(user_id=admin_id) & ~filters.COMMAND, relay_customer_message))
    app.add_error_handler(error_handler)
    LOG.info("Starting 658pay support bot with database at %s", DATABASE_PATH)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
