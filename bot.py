import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Pelayan Web untuk Render.com (Health Check) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Cikgu English Bot sedang aktif! Let's learn English!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Kandungan Bot (Belajar English dalam Bahasa Melayu) ---

LEARNING_CONTENT = [
    # Hari 1: Greetings (Salam & Teguran)
    "👋 *Hari 1: Ucapan Asas (Greetings)*\n\n"
    "Mari kita mulakan dengan cara menegur orang dalam English yang betul.\n\n"
    "*Contoh Utama:*\n"
    "- *Standard:* \"How are you?\" (Apa khabar?)\n"
    "- *Casual:* \"What's up?\" (Apa cerita/Apa khabar? - untuk kawan rapat)\n"
    "- *Response:* \"I'm good, thank you.\" (Saya baik, terima kasih.)\n\n"
    "*Tips Cikgu:* Elakkan cakap \"I fine\". Sebutan yang lebih natural ialah \"I'm doing well\" atau \"I'm good\".",

    # Hari 2: Essential Phrases (Ayat Penting)
    "🗣️ *Hari 2: Ayat Penting di Tempat Awam*\n\n"
    "Kadang-kadang kita segan nak minta tolong dalam English. Gunakan ayat ni:\n\n"
    "*Minta Tolong:*\n"
    "- \"Excuse me, could you help me?\" (Maafkan saya, boleh bantu saya?)\n"
    "- \"Where is the nearest toilet?\" (Di mana tandas terdekat?)\n\n"
    "*Order Makanan:*\n"
    "- \"I would like to have...\" (Saya mahu pesan...)\n"
    "- \"Can I have the bill, please?\" (Boleh saya dapatkan bil?)",

    # Hari 3: Manglish vs Standard English
    "🇬🇧 *Hari 3: Manglish vs Standard English*\n\n"
    "Kita selalu guna 'Lah' atau 'Can or not'. Jom tukar jadi lebih profesional!\n\n"
    "*Manglish:* \"I go first ah.\"\n"
    "*Standard:* \"I'll be going now.\" atau \"I'm leaving first.\"\n\n"
    "*Manglish:* \"Can or not?\"\n"
    "*Standard:* \"Is it possible?\" atau \"Can you do it?\"\n\n"
    "Jangan risau pasal accent, yang penting 'grammar' dan maksud sampai!"
]

QUIZ_DATA = [
    {
        "question": "Apakah cara yang lebih formal untuk bertanya 'Apa khabar'?",
        "options": ["What's up?", "How are you?", "You okay ah?"],
        "correct": 1
    },
    {
        "question": "Jika anda mahu memesan makanan, ayat manakah yang paling sesuai?",
        "options": ["I want eat this.", "I would like to order...", "Give me food."],
        "correct": 1
    },
    {
        "question": "Bagaimana cara menukar ayat 'Can or not?' kepada English yang lebih betul?",
        "options": ["Is it possible?", "Can or cannot?", "Sure can?"],
        "correct": 0
    }
]

# --- Logik Bot ---
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    keyboard = [
        ["Belajar English 📚", "Uji Minda (Quiz) 🧠"],
        ["Rehat Dulu ☕"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        f"Hello! Selamat Datang ke *Cikgu English Bot*! 👨‍🏫🇬🇧\n\n"
        "Saya akan bantu anda bercakap English dengan lebih yakin.\n"
        "Pilih menu di bawah untuk mulakan sesi hari ini."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "Belajar English 📚":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("Bagus! Anda dah belajar untuk hari ini. Balik esok untuk ilmu baru ya! 🌟")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day], parse_mode='Markdown')
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("Wow! Anda dah habiskan semua silibus buat masa ini. Syabas!")

    elif text == "Uji Minda (Quiz) 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Soalan Kuiz English:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Semua kuiz telah dijawab. Anda memang hebat dalam English! 🏆")

    elif text == "Rehat Dulu ☕":
        await update.message.reply_text("Okay, take a break! Nanti kita sambung belajar lagi. See you! 👋")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "Excellent! Jawapan anda betul. ✅\n\n"
    else:
        feedback = "Oh no, cuba lagi! Jangan putus asa.\n\n"
    
    feedback += "Praktis setiap hari untuk jadi lebih lancar! 🌟"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("RALAT: TELEGRAM_TOKEN tidak dijumpai.")
        exit(1)
    
    print("Memulakan Cikgu English Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
