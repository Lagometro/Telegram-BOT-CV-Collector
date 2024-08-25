import sqlite3
from telegram import Update, Contact, Document, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = 'your_token'
GROUP_CHAT_ID = 'you_chat_id'

ASK_NAME, ASK_CONTACT, ASK_RESUME, CONFIRM_SUBMISSION, REVIEW = range(5)

db_path = 'applications.db'

# Create a table to store questionnaires if it doesn’t already exist
def create_table():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS applications (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  full_name TEXT,
                  contact TEXT,
                  resume TEXT,
                  UNIQUE(full_name, contact)
              )
              ''')
    conn.commit()
    conn.close()

# Check if there is a questionnaire with the specified full name and contact details
def check_application_exists(full_name, contact):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
              SELECT id FROM applications
              WHERE full_name = ? AND contact = ?
              ''', (full_name, contact))
    result = c.fetchone()
    conn.close()
    return result is not None

# Adding the questionnaire to the database
def insert_application(full_name, contact, resume):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
              INSERT INTO applications (full_name, contact, resume)
              VALUES (?, ?, ?)
              ''', (full_name, contact, resume))
    conn.commit()
    inserted_id = c.lastrowid
    conn.close()
    return inserted_id

# Function to add "+" before phone number if it is missing
def format_phone_number(phone_number):
    if not phone_number.startswith('+'):
        return '+' + phone_number
    return phone_number

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[KeyboardButton("Fill the form")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Click «Fill the form» to get started.', reply_markup=reply_markup)
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Let\'s get to know each other: enter your first and last name👋🏻', reply_markup=ReplyKeyboardRemove())
    return ASK_NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text.strip()
    if ' ' not in full_name:
        await update.message.reply_text('Please enter your first and last name with a space.')
        return ASK_NAME

    context.user_data['full_name'] = full_name

# Create a button to request contact
    keyboard = [[KeyboardButton("Share a contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(f'{full_name}, leave your contact so we can contact you', reply_markup=reply_markup)
    return ASK_CONTACT

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    if contact:
# Formatting a phone number
        formatted_contact = format_phone_number(contact.phone_number)
        context.user_data['contact'] = formatted_contact

# Сheck if there is a profile with the same full name and contact information
        if check_application_exists(context.user_data['full_name'], context.user_data['contact']):
            await update.message.reply_text('You have already submitted an application with the same first and last name and contact details. Please submit only one application.')
            return ConversationHandler.END  # Ending the dialogue
        else:
            await update.message.reply_text('Super🔥 The last step remains - send your CV as a file', reply_markup=ReplyKeyboardRemove())
            return ASK_RESUME
    else:
        await update.message.reply_text('Please share your contact using the button below.')
        return ASK_CONTACT

async def ask_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    document = update.message.document
    if document:
        context.user_data['resume'] = document.file_id

# Show confirmation button
        keyboard = [[KeyboardButton("Send"), KeyboardButton("Start over")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        message_text = (
            f"Full name: {context.user_data['full_name']}\n"
            f"Contact: {context.user_data['contact']}\n\n"
            "Check the data and click «Send»."
        )

        await update.message.reply_text(message_text, reply_markup=reply_markup)
        await context.bot.send_document(
            chat_id=update.message.chat_id,
            document=context.user_data['resume'],
            caption="Your CV"
        )

        return REVIEW
    else:
        await update.message.reply_text('Please send your resume as a file.')
        return ASK_RESUME

async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
# Insert the questionnaire into the database
    insert_application(context.user_data['full_name'], context.user_data['contact'], context.user_data['resume'])

# We collect text to send to the group
    message_text = f"Full name: {context.user_data['full_name']}\nContact: {context.user_data['contact']}\n\n"
    await context.bot.send_document(
        chat_id=GROUP_CHAT_ID,
        document=context.user_data['resume'],
        caption=message_text
    )

    await update.message.reply_text('Congratulations, we already have your CV.🫡', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()  # Clear user data when done
    return ConversationHandler.END  # End the conversation

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    return await start(update, context)

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await update.message.reply_text(f'ID of this chat: {chat_id}')

def main():
    create_table()
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.Regex('^Fill the form$'), ask_name),
                       MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            ASK_CONTACT: [MessageHandler(filters.CONTACT, ask_contact)],
            ASK_RESUME: [MessageHandler(filters.Document.ALL, ask_resume)],
            REVIEW: [
                MessageHandler(filters.TEXT & filters.Regex('^Send$'), confirm_submission),
                MessageHandler(filters.TEXT & filters.Regex('^Start over$'), start_over)
            ],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('my_id', my_id))

    application.run_polling()

if __name__ == '__main__':
    main()
