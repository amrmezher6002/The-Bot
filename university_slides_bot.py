"""
╔══════════════════════════════════════════════════════╗
║       University Engineering Slides Bot              ║
║       Majors: Computer Engineering, Electrical       ║
╚══════════════════════════════════════════════════════╝

─── QUICK SETUP ────────────────────────────────────────

1. Install the library:
      pip install python-telegram-bot==20.7

2. Create your bot:
      • Open Telegram → search @BotFather
      • Send /newbot → follow the steps
      • Copy the token and paste it below in BOT_TOKEN

3. Run the bot:
      python university_slides_bot.py

─── HOW TO ADD SLIDES ──────────────────────────────────

Step 1 — Upload the file to your bot:
   • Start your bot, then send any PDF/PPT directly to it in chat.

Step 2 — Get the file_id:
   • While the bot is running it will print the file_id in the terminal.
   • OR visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
     and look for "file_id" inside the "document" field.

Step 3 — Add it to SLIDES_DATA below:
   {
       "title": "Lecture 1 – Introduction",
       "file_id": "BQACAgIAAxkBAAI..."   ← paste here
   }

────────────────────────────────────────────────────────
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ════════════════════════════════════════════════════════
#  🔑  YOUR BOT TOKEN  —  paste it between the quotes
# ════════════════════════════════════════════════════════
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ════════════════════════════════════════════════════════
#  📚  SLIDES DATA  —  add your subjects and file_ids here
#
#  Layout:
#  "Major" → "Subject" → list of slides
#
#  Each slide:
#  { "title": "Lecture X – Topic", "file_id": "XXXX..." }
#
#  Leave file_id as "" until you have the real one.
#  The bot will tell users "Coming soon" for empty ones.
# ════════════════════════════════════════════════════════

SLIDES_DATA = {
    "💻 Computer Engineering": {
        "Data Structures & Algorithms": [
            {"title": "Lecture 1 – Arrays & Linked Lists",  "file_id": ""},
            {"title": "Lecture 2 – Stacks & Queues",        "file_id": ""},
            {"title": "Lecture 3 – Trees & Graphs",         "file_id": ""},
            {"title": "Lecture 4 – Sorting Algorithms",     "file_id": ""},
        ],
        "Operating Systems": [
            {"title": "Lecture 1 – OS Overview",            "file_id": ""},
            {"title": "Lecture 2 – Processes & Threads",    "file_id": ""},
            {"title": "Lecture 3 – Memory Management",      "file_id": ""},
        ],
        "Computer Networks": [
            {"title": "Lecture 1 – Network Layers",         "file_id": ""},
            {"title": "Lecture 2 – TCP/IP",                 "file_id": ""},
            {"title": "Lecture 3 – Routing & Switching",    "file_id": ""},
        ],
        "Database Systems": [
            {"title": "Lecture 1 – ER Diagrams",            "file_id": ""},
            {"title": "Lecture 2 – SQL Basics",             "file_id": ""},
            {"title": "Lecture 3 – Normalization",          "file_id": ""},
        ],
    },
    "⚡ Electrical Engineering": {
        "Circuit Analysis": [
            {"title": "Lecture 1 – Basic Circuits",         "file_id": ""},
            {"title": "Lecture 2 – Kirchhoff's Laws",       "file_id": ""},
            {"title": "Lecture 3 – AC/DC Circuits",         "file_id": ""},
        ],
        "Signals & Systems": [
            {"title": "Lecture 1 – Signals Overview",       "file_id": ""},
            {"title": "Lecture 2 – Fourier Transform",      "file_id": ""},
            {"title": "Lecture 3 – Laplace Transform",      "file_id": ""},
        ],
        "Electromagnetics": [
            {"title": "Lecture 1 – Electric Fields",        "file_id": ""},
            {"title": "Lecture 2 – Magnetic Fields",        "file_id": ""},
            {"title": "Lecture 3 – Maxwell's Equations",    "file_id": ""},
        ],
        "Digital Electronics": [
            {"title": "Lecture 1 – Logic Gates",            "file_id": ""},
            {"title": "Lecture 2 – Combinational Circuits", "file_id": ""},
            {"title": "Lecture 3 – Sequential Circuits",    "file_id": ""},
        ],
    },
}

# ════════════════════════════════════════════════════════
#  BOT LOGIC — no need to edit below this line
# ════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── Keyboards ────────────────────────────────────────────

def kb_main_menu():
    rows = [[InlineKeyboardButton(major, callback_data=f"major|{major}")]
            for major in SLIDES_DATA]
    rows.append([InlineKeyboardButton("ℹ️ Help", callback_data="help")])
    return InlineKeyboardMarkup(rows)


def kb_subjects(major: str):
    rows = [[InlineKeyboardButton(f"📂 {subj}", callback_data=f"subj|{major}|{subj}")]
            for subj in SLIDES_DATA[major]]
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="main")])
    return InlineKeyboardMarkup(rows)


def kb_slides(major: str, subj: str):
    slides = SLIDES_DATA[major][subj]
    rows = []
    for i, s in enumerate(slides):
        label = f"📄 {s['title']}" if s["file_id"] else f"🔜 {s['title']} (coming soon)"
        rows.append([InlineKeyboardButton(label, callback_data=f"slide|{major}|{subj}|{i}")])
    rows.append([InlineKeyboardButton(f"⬅️ Back", callback_data=f"major|{major}")])
    return InlineKeyboardMarkup(rows)


# ── Handlers ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Engineering Slides Bot*\n\n"
        "Welcome! Browse and download university lecture slides "
        "organized by major and subject.\n\n"
        "👇 Choose your major to get started:",
        parse_mode="Markdown",
        reply_markup=kb_main_menu(),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Main menu
    if data == "main":
        await query.edit_message_text(
            "👇 Choose your major:",
            reply_markup=kb_main_menu(),
        )

    # Help
    elif data == "help":
        await query.edit_message_text(
            "ℹ️ *How to use this bot*\n\n"
            "1️⃣ Pick your *major*\n"
            "2️⃣ Choose a *subject*\n"
            "3️⃣ Tap a lecture to *download the slides*\n\n"
            "Slides marked 🔜 are coming soon.\n"
            "Type /start anytime to return to the main menu.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Back", callback_data="main")]]
            ),
        )

    # Major selected
    elif data.startswith("major|"):
        major = data.split("|", 1)[1]
        if major not in SLIDES_DATA:
            await query.edit_message_text("❌ Major not found.")
            return
        count = len(SLIDES_DATA[major])
        await query.edit_message_text(
            f"*{major}*\n\n{count} subjects available — choose one:",
            parse_mode="Markdown",
            reply_markup=kb_subjects(major),
        )

    # Subject selected
    elif data.startswith("subj|"):
        _, major, subj = data.split("|", 2)
        if major not in SLIDES_DATA or subj not in SLIDES_DATA[major]:
            await query.edit_message_text("❌ Subject not found.")
            return
        count = len(SLIDES_DATA[major][subj])
        await query.edit_message_text(
            f"*{subj}*\n\n{count} lecture(s) available:",
            parse_mode="Markdown",
            reply_markup=kb_slides(major, subj),
        )

    # Slide selected
    elif data.startswith("slide|"):
        _, major, subj, idx_str = data.split("|", 3)
        slide = SLIDES_DATA[major][subj][int(idx_str)]

        if not slide["file_id"]:
            await query.answer("🔜 This slide hasn't been uploaded yet.", show_alert=True)
            return

        await query.answer("📤 Sending file...")
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=slide["file_id"],
            caption=f"📄 *{slide['title']}*\n_{subj}_  •  _{major}_",
            parse_mode="Markdown",
        )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    When you send a file directly to the bot, it prints the file_id
    in the terminal so you can copy-paste it into SLIDES_DATA above.
    """
    doc = update.message.document
    if doc:
        file_id = doc.file_id
        print(f"\n✅ FILE RECEIVED")
        print(f"   Name    : {doc.file_name}")
        print(f"   file_id : {file_id}\n")
        await update.message.reply_text(
            f"✅ *File received!*\n\n"
            f"Copy this `file_id` and paste it into `SLIDES_DATA` in the bot code:\n\n"
            f"`{file_id}`",
            parse_mode="Markdown",
        )


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Use /start to open the main menu."
    )


# ── Main ──────────────────────────────────────────────────

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  Set your BOT_TOKEN first, then run the bot again.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))

    print("🤖 Bot is running! Press Ctrl+C to stop.")
    print("📁 Send any file to the bot to get its file_id.\n")
    app.run_polling()


if __name__ == "__main__":
    main()