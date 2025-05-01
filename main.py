import random import logging import pytz from datetime import datetime from telegram import ( Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove ) from telegram.constants import ChatAction from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler )

Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

States for conversation

captcha_codes = {} user_balances = {} user_referrals = {} user_language = {} WITHDRAW_AMOUNT, WITHDRAW_METHOD, WITHDRAW_NUMBER = range(3)

LANGUAGES = { "bn": "বাংলা", "en": "English", "hi": "हिंदी", "zh": "中文", "ja": "日本語", "ar": "العربية" }

Utility

async def send_typing(context): await context.bot.send_chat_action(chat_id=context.effective_chat.id, action=ChatAction.TYPING)

def get_time_bangladesh(): tz = pytz.timezone("Asia/Dhaka") return datetime.now(tz).strftime('%Y-%m-%d %H:%M')

Start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user code = random.randint(1000, 9999) captcha_codes[user.id] = str(code)

# Handle referral
if context.args:
    referrer_id = int(context.args[0])
    if referrer_id != user.id:
        referrals = user_referrals.setdefault(referrer_id, [])
        if user.id not in referrals:
            referrals.append(user.id)
            user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 50

keyboard = InlineKeyboardButton(str(code), callback_data=f"captcha:{code}")
await update.message.reply_text("CAPTCHA: নিচের সংখ্যাটি নির্বাচন করুন:",
                                reply_markup=InlineKeyboardMarkup(keyboard))

Captcha Handler

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
        await query.edit_message_text("❌ ভুল হয়েছে। আবার চেষ্টা করুন:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))

Main Menu

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("👤 Profile", callback_data="profile"), InlineKeyboardButton("💸 Refer & Earn", callback_data="refer")], [InlineKeyboardButton("👥 Team Member", callback_data="team"), InlineKeyboardButton("💡 Earn Tips", callback_data="tips")], [InlineKeyboardButton("🏧 Withdraw Cash", callback_data="withdraw")], [InlineKeyboardButton("🛠 Support", callback_data="support"), InlineKeyboardButton("🌐 Language", callback_data="language")], ] await context.bot.send_message(chat_id=update.effective_chat.id, text="নিচের মেনু থেকে একটি বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))

Profile

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user balance = user_balances.get(user.id, 0) text = ( f"👤 Name: {user.full_name}\n" f"🆔 User ID: {user.id}\n" f"💰 Balance: {balance}৳\n" f"📅 Joined: {get_time_bangladesh()}" ) await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_keyboard())

Refer & Earn

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user ref_link = f"https://t.me/{context.bot.username}?start={user.id}" msg = ( f"👤 Name: {user.full_name}\n🆔 ID: {user.id}\n\n" f"🔗 Your Referral Link:\n{ref_link}\n\n" "প্রতি সফল রেফারে ৫০ টাকা যোগ হবে। বেশি বেশি শেয়ার করুন!" ) await query.edit_message_text(msg, reply_markup=back_keyboard())

Team Member

async def show_team(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user = query.from_user team = user_referrals.get(user.id, []) member_list = "\n".join([f"- {m}" for m in team]) if team else "No members yet." msg = f"👥 Team of {user.full_name}\n👤 Total Referrals: {len(team)}\n\n{member_list}" await query.edit_message_text(msg, reply_markup=back_keyboard())

Back button

def back_keyboard(): return InlineKeyboardMarkup(InlineKeyboardButton("🔙 Back", callback_data="back"))

Withdraw

async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.edit_message_text("উত্তোলনের পরিমাণ লিখুন (৳):") return WITHDRAW_AMOUNT

async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user try: amount = int(update.message.text) balance = user_balances.get(user.id, 0) if amount > balance: await update.message.reply_text("❌ পর্যাপ্ত ব্যালেন্স নেই।") return ConversationHandler.END context.user_data['amount'] = amount await update.message.reply_text("পেমেন্ট পদ্ধতি নির্বাচন করুন: বিকাশ / নগদ / রকেট / উপায়") return WITHDRAW_METHOD except ValueError: await update.message.reply_text("সংখ্যা দিন সঠিকভাবে।") return WITHDRAW_AMOUNT

async def withdraw_method(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data['method'] = update.message.text await update.message.reply_text("আপনার নাম্বার দিন:") return WITHDRAW_NUMBER

async def withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE): number = update.message.text user = update.effective_user amount = context.user_data['amount'] method = context.user_data['method'] user_balances[user.id] = user_balances.get(user.id, 0) - amount await update.message.reply_text( f"✅ উত্তোলনের অনুরোধ গ্রহণ করা হয়েছে।\n\nমেথড: {method}\nনাম্বার: {number}\nপরিমাণ: {amount}৳\n\nঅপেক্ষা করুন।") return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("বাতিল করা হয়েছে।", reply_markup=ReplyKeyboardRemove()) return ConversationHandler.END

Support

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("যেকোনো প্রকার সমস্যা হলে যোগাযোগ করুন: https://t.me/U011111111", reply_markup=back_keyboard())

Language

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")] for code, name in LANGUAGES.items()] await update.callback_query.edit_message_text("ভাষা পরিবর্তন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user_id = query.from_user.id lang_code = query.data.split("_")[1] user_language[user_id] = lang_code await query.edit_message_text(f"✅ ভাষা পরিবর্তন হয়েছে: {LANGUAGES[lang_code]}", reply_markup=back_keyboard())

Callback Router

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE): data = update.callback_query.data if data == "profile": await show_profile(update, context) elif data == "refer": await refer_earn(update, context) elif data == "team": await show_team(update, context) elif data == "tips": await earn_tips(update, context) elif data.startswith("tip_"): await tips_handler(update, context) elif data == "withdraw": return await withdraw_start(update, context) elif data == "support": await support(update, context) elif data == "language": await language(update, context) elif data.startswith("lang_"): await set_language(update, context) elif data == "back": await show_main_menu(update, context)

Earn Tips (same as before)

async def earn_tips(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query buttons = [ [InlineKeyboardButton("1. Gmail Account Sale", callback_data="tip_gmail")], [InlineKeyboardButton("2. WhatsApp Number Sale", callback_data="tip_whatsapp")], [InlineKeyboardButton("3. BDT Game", callback_data="tip_bdtgame")], [InlineKeyboardButton("4. All Types Web&App Buy", callback_data="tip_webapp")], [InlineKeyboardButton("🔙 Back", callback_data="back")], ] await query.edit_message_text("Earn Tips Menu:", reply_markup=InlineKeyboardMarkup(buttons))

async def tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query tips = { "tip_gmail": ("📱 মোবাইল ফোন এর মাধ্যমে জিমেইল একাউন্ট তৈরি করে বিক্রি করুন এবং টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link1.com"), "tip_whatsapp": ("📱 মোবাইল ফোন এর মাধ্যমে Whatsapp একাউন্ট তৈরি করে বিক্রি করুন এবং টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link2.com"), "tip_bdtgame": ("📱 মোবাইল ফোন এর মাধ্যমে BDT GAME খেলে  টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link3.com"), "tip_webapp": ("স্বল্প মূল্যে সকল প্রকার Web+App+Bot তৈরি করে ইনকাম শুরু করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link4.com") } msg, url = tips[query.data] await query.edit_message_text(f"{msg}\n\n{url}", reply_markup=back_keyboard())

Main

def main(): TOKEN = "7343006860:AAEzZkUuwM_3nfXWqyMG6ZORnlrYvmtewcI" app = Application.builder().token(TOKEN).build()

withdraw_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(withdraw_start, pattern="^withdraw$")],
    states={
        WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount)],
        WITHDRAW_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_method)],
        WITHDRAW_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_number)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^captcha:"))
app.add_handler(CallbackQueryHandler(callback_router))
app.add_handler(withdraw_conv)

app.run_polling()

if name == "main": main()

