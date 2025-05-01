import os
import random
import logging
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# Environment variables (optional, if needed)
TOKEN = "7343006860:AAEzZkUuwM_3nfXWqyMG6ZORnlrYvmtewcI"  # Add your bot token here
ADMIN_ID = 6243881362  # Add your admin ID here

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation
captcha_codes = {}
WITHDRAW_AMOUNT, WITHDRAW_METHOD, WITHDRAW_NUMBER = range(3)

# Memory storage for user data
users_data = {}

# Utility functions
async def send_typing(context):
    await context.bot.send_chat_action(chat_id=context.effective_chat.id, action=ChatAction.TYPING)

async def get_or_create_user(user):
    # Create a new user in memory if not exists
    if user.id not in users_data:
        users_data[user.id] = {
            "name": user.full_name,
            "id": user.id,
            "balance": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ref": None,
            "ref_count": 0,
            "team": [],
        }
    return users_data[user.id]

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await get_or_create_user(user)
    code = random.randint(1000, 9999)
    captcha_codes[user.id] = str(code)
    keyboard = InlineKeyboardButton(str(code), callback_data=f"captcha:{code}")
    await update.message.reply_text("CAPTCHA: নিচের সংখ্যাটি নির্বাচন করুন:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

# Captcha Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

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

# Main Menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👤 Profile", callback_data="profile"),
         InlineKeyboardButton("💸 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("👥 Team Member", callback_data="team"),
         InlineKeyboardButton("💡 Earn Tips", callback_data="tips")],
        [InlineKeyboardButton("🏧 Withdraw Cash", callback_data="withdraw")],
        [InlineKeyboardButton("🛠 Support", callback_data="support"),
         InlineKeyboardButton("🌐 Language", callback_data="language")],
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="নিচের মেনু থেকে একটি বেছে নিন:",
                                   reply_markup=InlineKeyboardMarkup(keyboard))

# Profile
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_data = users_data.get(user.id, {})
    text = (
        f"👤 Name: {user_data['name']}\n"
        f"🆔 User ID: {user_data['id']}\n"
        f"💰 Balance: {user_data['balance']} ৳\n"
        f"📅 Joined: {user_data['joined']}"
    )
    await query.edit_message_text(text=text, parse_mode="Markdown")

# Refer & Earn
async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
    user_data = users_data.get(user.id, {})
    msg = (
        f"👤 Name: {user_data['name']}\n🆔 ID: {user.id}\n\n"
        f"🔗 Your Referral Link:\n{ref_link}\n\n"
        "প্রতি সফল রেফারে ৫০ টাকা যোগ হবে। বেশি বেশি শেয়ার করুন!"
    )
    await query.edit_message_text(msg)

# Team Member
async def show_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_data = users_data.get(user.id, {})
    team = user_data.get("team", [])
    member_list = "\n".join([f"- {m}" for m in team]) if team else "No members yet."
    msg = f"👥 Team of {user_data['name']}\n👤 Total Referrals: {len(team)}\n\n{member_list}"
    await query.edit_message_text(msg)

# Earn Tips
async def earn_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    buttons = [
        [InlineKeyboardButton("1. Gmail Account Sale", callback_data="tip_gmail")],
        [InlineKeyboardButton("2. WhatsApp Number Sale", callback_data="tip_whatsapp")],
        [InlineKeyboardButton("3. BDT Game", callback_data="tip_bdtgame")],
        [InlineKeyboardButton("4. All Types Web&App Buy", callback_data="tip_webapp")],
    ]
    await query.edit_message_text("Earn Tips Menu:", reply_markup=InlineKeyboardMarkup(buttons))

# Tip Messages
async def tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tips = {
        "tip_gmail": ("📱 মোবাইল ফোন এর মাধ্যমে জিমেইল একাউন্ট তৈরি করে বিক্রি করুন এবং টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link1.com"),
        "tip_whatsapp": ("📱 মোবাইল ফোন এর মাধ্যমে Whatsapp একাউন্ট তৈরি করে বিক্রি করুন এবং টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link2.com"),
        "tip_bdtgame": ("📱 মোবাইল ফোন এর মাধ্যমে BDT GAME খেলে  টাকা উপার্জন করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link3.com"),
        "tip_webapp": ("স্বল্প মূল্যে সকল প্রকার Web+App+Bot তৈরি করে ইনকাম শুরু করতে নিচের লিংকে ক্লিক করুন ♻️", "https://link4.com")
    }
    msg, url = tips[query.data]
    await query.edit_message_text(f"{msg}\n\n{url}")

# Withdraw Conversation
async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = users_data.get(query.from_user.id, {})
    if user_data['balance'] < 1000:
        await query.edit_message_text(f"❌ আপনার ব্যালেন্স {user_data['balance']}৳। উত্তোলন করতে আপনার প্রয়োজন ১০০০৳।")
        return ConversationHandler.END
    await query.edit_message_text("উত্তোলনের পরিমাণ লিখুন (৳):")
    return WITHDRAW_AMOUNT

async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = int(update.message.text)
    await update.message.reply_text("পেমেন্ট পদ্ধতি নির্বাচন করুন: বিকাশ / নগদ / রকেট / উপায়")
    return WITHDRAW_METHOD

async def withdraw_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['method'] = update.message.text
    await update.message.reply_text("আপনার নাম্বার দিন:")
    return WITHDRAW_NUMBER

async def withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    number = update.message.text
    amount = context.user_data['amount']
    method = context.user_data['method']

    # Update balance in memory
    if user_id in users_data:
        users_data[user_id]["balance"] -= amount

    await update.message.reply_text(
        f"✅ উত্তোলনের অনুরোধ গ্রহণ করা হয়েছে।\n\nমেথড: {method}\nনাম্বার: {number}\nপরিমাণ: {amount}৳\n\nঅপেক্ষা করুন।")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("বাতিল করা হয়েছে।", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Support & Language
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("যেকোনো প্রকার সমস্যা হলে যোগাযোগ করুন: https://t.me/U011111111")

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("ভাষা পরিবর্তন Coming Soon...")

# Callback Router
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "profile":
        await show_profile(update, context)
    elif data == "refer":
        await refer_earn(update, context)
    elif data == "team":
        await show_team(update, context)
    elif data == "tips":
        await earn_tips(update, context)
    elif data.startswith("tip_"):
        await tips_handler(update, context)
    elif data == "withdraw":
        await withdraw_start(update, context)
    elif data == "support":
        await support(update, context)
    elif data == "language":
        await language(update, context)

# Main Function
def main():
    app = Application.builder().token(TOKEN).build()

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

if __name__ == "__main__":
    main()
