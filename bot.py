#!/usr/bin/env python3
"""
HookInfo Telegram Bot — V5 Final
Uses polling (simple & reliable) + Flask health check for Render & UptimeRobot
"""

import logging
import os
import sys
import threading

print("==> bot.py started", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8742784444:AAEh21SKiukT9zIlojpuCKbKD3sPp2cs5mw")
PORT      = int(os.environ.get("PORT", 10000))

print(f"==> Python: {sys.version}", flush=True)
print(f"==> PORT: {PORT}", flush=True)

# ─── HEALTH CHECK SERVER (keeps Render + UptimeRobot happy) ──────────────────
def run_health_server():
    try:
        from flask import Flask
        app = Flask(__name__)

        @app.route("/")
        def health():
            return "HookInfo Bot is running!", 200

        @app.route("/health")
        def healthcheck():
            return "OK", 200

        print(f"==> Health server starting on port {PORT}", flush=True)
        app.run(host="0.0.0.0", port=PORT)
    except Exception as e:
        print(f"==> Health server error: {e}", flush=True)

# Start health server in background thread
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# ─── TELEGRAM BOT ────────────────────────────────────────────────────────────
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler,
        CallbackQueryHandler, ContextTypes, ConversationHandler, filters
    )
    print("==> Telegram imports OK", flush=True)
except Exception as e:
    print(f"==> IMPORT ERROR: {e}", flush=True)
    sys.exit(1)

# ─── STATES ──────────────────────────────────────────────────────────────────
CHOOSING, INSTAGRAM, WEBSEARCH, PHONE, IPLOOKUP, USERNAME = range(6)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ─── KEYBOARDS ───────────────────────────────────────────────────────────────

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📸  Instagram OSINT",  callback_data="instagram")],
        [InlineKeyboardButton("🌐  Web Search",        callback_data="websearch")],
        [InlineKeyboardButton("📞  Phone Lookup",      callback_data="phone")],
        [InlineKeyboardButton("🖥️   IP Lookup",        callback_data="iplookup")],
        [InlineKeyboardButton("🔍  Username Search",   callback_data="username")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="menu")]
    ])


# ─── HANDLERS ────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️ *HookInfo Bot — V 1.0*\n"
        "_OSINT Tool by Hookinfo_\n\n"
        "Hookinfo will not be responsible for the loss you have made.\n"
        "By using this bot you agree that *you* are responsible.\n\n"
        "Choose a feature:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "menu":
        await query.edit_message_text(
            "🕵️ *HookInfo Bot — Main Menu*\nChoose a feature:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return CHOOSING

    prompts = {
        "instagram": (INSTAGRAM, "📸 *Instagram OSINT*\n\nEnter an Instagram *username* (without @):\nExample: `cristiano`"),
        "websearch": (WEBSEARCH, "🌐 *Web Search*\n\nEnter your *search query*:\nExample: `Elon Musk net worth`"),
        "phone":     (PHONE,     "📞 *Phone Lookup*\n\nEnter a phone number with *country code*:\nExample: `+14155552671`"),
        "iplookup":  (IPLOOKUP,  "🖥️ *IP Lookup*\n\nEnter an *IP address*:\nExample: `8.8.8.8`"),
        "username":  (USERNAME,  "🔍 *Username Search*\n\nEnter a *username* to search across 15 platforms:\nExample: `johndoe`"),
    }

    if data in prompts:
        state, prompt = prompts[data]
        context.user_data["feature"] = data
        await query.edit_message_text(
            prompt,
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        return state

    return CHOOSING


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from hookinfo import (
        instagram_check, web_search, phone_lookup,
        ip_lookup, username_search
    )

    text    = update.message.text.strip()
    feature = context.user_data.get("feature", "")

    await update.message.reply_text("⏳ Fetching data, please wait...")

    dispatch = {
        "instagram": lambda: instagram_check(text),
        "websearch":  lambda: web_search(text),
        "phone":      lambda: phone_lookup(text),
        "iplookup":   lambda: ip_lookup(text),
        "username":   lambda: username_search(text),
    }

    func = dispatch.get(feature)
    if func:
        try:
            result = func()
        except Exception as e:
            result = f"❌ Something went wrong.\nError: `{e}`"
    else:
        result = "❓ Unknown feature. Go back to the menu."

    await update.message.reply_text(
        result,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=back_keyboard()
    )
    return CHOOSING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Cancelled. Type /start to begin again.")
    return ConversationHandler.END


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("==> Building Telegram app...", flush=True)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING:   [CallbackQueryHandler(menu_callback)],
            INSTAGRAM:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input), CallbackQueryHandler(menu_callback)],
            WEBSEARCH:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input), CallbackQueryHandler(menu_callback)],
            PHONE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input), CallbackQueryHandler(menu_callback)],
            IPLOOKUP:   [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input), CallbackQueryHandler(menu_callback)],
            USERNAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input), CallbackQueryHandler(menu_callback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv)

    print("==> Starting polling...", flush=True)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"==> FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
