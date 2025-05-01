import random import logging from datetime import datetime from pytz import timezone from telegram import ( Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove ) from telegram.constants import ChatAction from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler )

Enable logging

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO ) logger = logging.getLogger(name)

States for conversation

WITHDRAW_AMOUNT, WITHDRAW_METHOD, WITHDRAW_NUMBER = range(3)

Temporary storage (in-memory)

captcha_codes = {} user_balances = {} user_languages = {}

Utilities

async def send_typing(context): await context.bot.send_chat_action(chat_id=context.effective_chat.id, action=ChatAction.TYPING)

Start with CAPTCHA

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user code = random.randint(1000, 9999) captcha_codes[user.id] = str(code) keyboard = InlineKeyboardButton(str(code), callback_data=f"captcha:{code}") await update.message.reply_text("CAPTCHA: নিচের সংখ্যাটি নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

Captcha handler

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() user = query.from_user data = query.data

if data.startswith("captcha:"):
    value = data.split(":")[1]
    correct = captcha_codes.get(user.id)
    if value == correct:
        del captcha_codes[user.id]
        await query.edit_message_text("✅ সঠিক! Bot চালু হলো।")
        await show_main_menu(update, context)
    else:
        new_code = str(random.randint(1000, 9999))
        captcha_codes[user.id] = new_code
        keyboard = InlineKeyboardButton(new_code, callback_data=f"captcha:{new_code}")
        await query.edit_message_text("❌ ভুল হয়েছে। আবার চেষ্টা করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

Main menu

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("\U0001F464 Profile", callback_data="profile"), InlineKeyboardButton("\U0001F4B8 Refer & Earn", callback_data="refer")], [InlineKeyboardButton("\U0001F465 Team Member", callback_data="team"), InlineKeyboardButton("\U0001F4A1 Earn Tips", callback_data="tips")], [InlineKeyboardButton("\U0001F3E7 Withdraw Cash", callback_data="withdraw")], [InlineKeyboardButton("\U0001F6E0 Support", callback_data="support"), InlineKeyboardButton("\U0001F310 Language", callback_data="language")], ] await context.bot.send_message(chat_id=update.effective_chat.id, text="নিচের মেনু থেকে একটি বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))

Profile

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user bd_time = datetime.now(timezone('Asia/Dhaka')).strftime('%Y-%m-%d %H:%M') balance = user_balances.get(user.id, 0) text = (f"\U0001F464 Name: {user.full_name}\n" f"\U0001F194 User ID: {user.id}\n" f"\U0001F4B0 Balance: {balance}৳\n" f"\U0001F4C5 Joined: {bd_time}") keyboard = InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu") await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

Refer & Earn

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user ref_link = f"https://t.me/{context.bot.username}?start={user.id}" user_balances[user.id] = user_balances.get(user.id, 0) msg = (f"\U0001F464 Name: {user.full_name}\n\U0001F194 ID: {user.id}\n\n" f"\U0001F517 Your Referral Link:\n{ref_link}\n\n" "প্রতি সফল রেফারে ৫০ টাকা যোগ হবে। বেশি বেশি শেয়ার করুন!") keyboard = InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu") await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

Team (Dummy)

async def show_team(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query team = ["User 1", "User 2"] msg = f"\U0001F465 Team Members:\n" + "\n".join([f"- {m}" for m in team]) keyboard = InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu") await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

Earn Tips

async def earn_tips(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query buttons = [ [InlineKeyboardButton("1. Gmail Account Sale", callback_data="tip_gmail")], [InlineKeyboardButton("2. WhatsApp Number Sale", callback_data="tip_whatsapp")], [InlineKeyboardButton("3. BDT Game", callback_data="tip_bdtgame")], [InlineKeyboardButton("4. All Types Web&App Buy", callback_data="tip_webapp")], [InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu")] ] await query.edit_message_text("Earn Tips Menu:", reply_markup=InlineKeyboardMarkup(buttons))

async def tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query tips = { "tip_gmail": ("\U0001F4F1 Gmail একাউন্ট তৈরি করে বিক্রি করুন:", "https://link1.com"), "tip_whatsapp": ("\U0001F4F1 Whatsapp একাউন্ট তৈরি করে বিক্রি করুন:", "https://link2.com"), "tip_bdtgame": ("\U0001F4F1 BDT Game খেলে আয় করুন:", "https://link3.com"), "tip_webapp": ("\U0001F4F1 Web & App তৈরি করে আয় করুন:", "https://link4.com") } msg, url = tips[query.data] keyboard = InlineKeyboardButton("\U0001F519 Back", callback_data="tips") await query.edit_message_text(f"{msg}\n\n{url}", reply_markup=InlineKeyboardMarkup(keyboard))

Withdraw

async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("উত্তোলনের পরিমাণ লিখুন (৳):") return WITHDRAW_AMOUNT

async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data['amount'] = int(update.message.text) await update.message.reply_text("পেমেন্ট পদ্ধতি লিখুন: বিকাশ / নগদ / রকেট / উপায়") return WITHDRAW_METHOD

async def withdraw_method(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data['method'] = update.message.text await update.message.reply_text("আপনার নাম্বার দিন:") return WITHDRAW_NUMBER

async def withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE): number = update.message.text amount = context.user_data['amount'] method = context.user_data['method'] await update.message.reply_text( f"✅ উত্তোলনের অনুরোধ গ্রহণ করা হয়েছে।\n\nমেথড: {method}\nনাম্বার: {number}\nপরিমাণ: {amount}৳") return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("বাতিল করা হয়েছে।", reply_markup=ReplyKeyboardRemove()) return ConversationHandler.END

Support & Language

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("যোগাযোগ: https://t.me/U011111111", reply_markup=InlineKeyboardMarkup(InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu")))

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("বাংলা", callback_data="lang_bn")], [InlineKeyboardButton("English", callback_data="lang_en")], [InlineKeyboardButton("हिन्दी", callback_data="lang_hi")], [InlineKeyboardButton("中文", callback_data="lang_zh")], [InlineKeyboardButton("日本語", callback_data="lang_ja")], [InlineKeyboardButton("العربية", callback_data="lang_ar")], [InlineKeyboardButton("\U0001F519 Back", callback_data="main_menu")] ] await update.callback_query.edit_message_text("ভাষা নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

Callback router

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE): data = update.callback_query.data if data == "profile": await show_profile(update, context) elif data == "refer": await refer_earn(update, context) elif data == "team": await show_team(update, context) elif data == "tips": await earn_tips(update, context) elif data.startswith("tip_"): await tips_handler(update, context) elif data == "withdraw": await withdraw_start(update, context) elif data == "support": await support(update, context) elif data == "language": await language(update, context) elif data.startswith("lang_"): user_languages[update.effective_user.id] = data.split("_")[1] await update.callback_query.edit_message_text("✅ ভাষা পরিবর্তন হয়েছে।") await show_main_menu(update, context) elif data == "main_menu": await show_main_menu(update, context)

Main

def main(): TOKEN = "7343006860:AAEzZkUuwM_3nfXWqyMG6ZORnlrYvmtewcI" app = Application.builder().token(TOKEN).build()

withdraw_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(withdraw_start, pattern="^withdraw$")],
    states={
        WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount)],
        WITHDRAW_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_method)],
        WITHDRAW_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_number)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^captcha:"))
app.add_handler(CallbackQueryHandler(callback_router))
app.add_handler(withdraw_conv)

app.run_polling()

if name == "main": main()

