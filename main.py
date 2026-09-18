import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ============================================================
# 658pay Telegram Bot
# Railway / Python / python-telegram-bot 21.6
#
# Railway Variables:
# BOT_TOKEN        = BotFather 提供的完整 Token
# WEBSITE_URL      = 网站完整 HTTPS 地址（可选，不填使用下面默认地址）
# WEBHOOK_SECRET   = 可选；本版本使用 Polling，不依赖它
#
# 说明：
# - 本版本使用 Telegram Polling，部署到 Railway 后无需 setup.ps1。
# - Railway 只要保持服务运行，机器人即可工作。
# - 不需要 Cloudflare Worker 的 fetch(request, env) 结构。
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBSITE_URL = os.getenv(
    "WEBSITE_URL",
    "https://jianzhi.jianzhi710731.workers.dev/",
).strip()

CHANNEL_URL = "https://t.me/dnyxw006"
SUPPORT_URL = "https://t.me/ID658pay"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# 主菜单
# ============================================================

def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🌐 打开网站", url=WEBSITE_URL),
        ],
        [
            InlineKeyboardButton("📢 进入 TG 频道", url=CHANNEL_URL),
        ],
        [
            InlineKeyboardButton("💬 联系客服 @ID658pay", url=SUPPORT_URL),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


START_TEXT = (
    "欢迎使用 658pay\n\n"
    "请选择下方入口：\n"
    "🌐 网站：查看介绍和任务演示\n"
    "📢 TG 频道：@dnyxw006\n"
    "💬 联系客服：@ID658pay"
)


HELP_TEXT = (
    "658pay 使用帮助\n\n"
    "/start 或 /menu：显示入口\n"
    "/website：网站\n"
    "/channel：频道\n"
    "/support：客服\n"
    "/help：帮助\n\n"
    "点击下方按钮即可打开相应页面。\n"
    "此机器人不会代办付款，也不会索取密码、PIN 或验证码。"
)


# ============================================================
# 指令
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        START_TEXT,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        START_TEXT,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def website_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = "点击下方“打开网站”查看 658pay 网站。"
    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def channel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = "TG 频道：@dnyxw006\n点击下方按钮打开频道。"
    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = "客服账号：@ID658pay\n点击下方“联系客服”进入聊天。"
    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


# ============================================================
# 普通文字消息
# ============================================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    # 只对私聊回复，群组中不主动响应
    if update.effective_chat and update.effective_chat.type != "private":
        return

    await update.message.reply_text(
        START_TEXT,
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


# ============================================================
# 错误处理
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Telegram Bot error: %s", context.error)


# ============================================================
# 主入口
# ============================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN 环境变量未设置！请在 Railway → Variables 中添加 BOT_TOKEN。"
        )

    if not WEBSITE_URL.startswith("https://"):
        raise RuntimeError(
            "WEBSITE_URL 必须是完整的 HTTPS 地址。"
        )

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_cmd))
    application.add_handler(CommandHandler("website", website_cmd))
    application.add_handler(CommandHandler("channel", channel_cmd))
    application.add_handler(CommandHandler("support", support_cmd))
    application.add_handler(CommandHandler("help", help_cmd))

    # 普通文字消息
    from telegram.ext import MessageHandler, filters
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    )

    application.add_error_handler(error_handler)

    logger.info("658pay Telegram Bot 正在启动...")
    logger.info("Website: %s", WEBSITE_URL)
    logger.info("Channel: %s", CHANNEL_URL)
    logger.info("Support: %s", SUPPORT_URL)

    # Railway 上直接 Polling。
    # 不需要 setup.ps1，不需要手动设置 Telegram Webhook。
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
