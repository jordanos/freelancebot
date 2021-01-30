from config import *
import logging
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, CallbackQueryHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Contact, ParseMode
from lang_dict import *
from backend import Db, Formatter
import re

db = Db(db_host, db_port, db_user, db_password, db_database)
fm = Formatter()

TITLE, DISCRIPTION = range(2)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class Bot():
    # initialize the bot with the bot token
    def __init__(self, token:str) -> None:
        self.bot_token = token

    # send message to a user 
    def show_message(self, update: Update, context: CallbackContext, text: str, chat_id: int=None, parse: ParseMode=None):
        if chat_id == None:
            if parse == None:
                update.message.reply_text(text)
            else :
                update.message.reply_text(text, parse_mode=parse)
        else:
            if parse == None:
                context.bot.sendMessage(chat_id, text)
            else:
                context.bot.sendMessage(chat_id, text, parse_mode=parse)

    # sends a message with reply markup text to a specific chat
    def keyboard(self, update: Update, context: CallbackContext, text: str, keyboard: list, one_time: bool, chat_id: int=None, parse: ParseMode=None) -> None:
        if chat_id == None:
            if parse == None:
                update.message.reply_text(
                    text=text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=one_time, resize_keyboard=True)
                )
            else:
                update.message.reply_text(
                    text=text, parse_mode=parse, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=one_time, resize_keyboard=True)
                )

        else:
            if parse == None:
                context.bot.sendMessage(chat_id=chat_id,
                    text=text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=one_time, resize_keyboard=True)
                )
            else:
                context.bot.sendMessage(chat_id=chat_id,
                    text=text, parse_mode=parse, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=one_time, resize_keyboard=True)
                )

    # sends inline keyboard message to a specific chat 
    def inline_keyboard(self, update: Update, context: CallbackContext, text: str, keyboard: list, chat_id: int=None, parse: ParseMode=None) -> None:
        inline_keyboard = []
        # parse the keyboard list 
        for row in keyboard:
            new_col = []
            for col in row:
                new_col.append(InlineKeyboardButton(text=col[0], callback_data=col[1]))
            inline_keyboard.append(new_col)

        if chat_id == None:
            if parse == None:
                update.message.reply_text(
                    text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )
            else:
                update.message.reply_text(
                    text=text, parse_mode=parse, reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )
        else:
            if parse == None:
                context.bot.sendMessage(
                    chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )
            else:
                context.bot.sendMessage(
                    chat_id=chat_id, text=text, parse_mode=parse, reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )

        
class Freelance(Bot):
    def __init__(self, bot_token: str) -> None:
        super().__init__(bot_token)
    
    def get_lang(self, chat_id: int=None) -> str:
        if chat_id == None:
            return "eng" 
        else:
            return "eng"

    def start_bot(self):
        # start running the bot
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(self.bot_token, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        command_start = CommandHandler("start", self.start)

        # Regex handler to handle specific texts
        regex_register = RegexHandler("^({})$".format(button_register["eng"]), self.is_user_registered)
        regex_login_freelancer = RegexHandler("^({})$".format(button_login_freelancer["eng"]), self.freelancer_menu)
        regex_login_employer = RegexHandler("^({})$".format(button_login_employer["eng"]), self.employer_menu)
        regex_profile = RegexHandler("^({})$".format(button_profile["eng"]), self.profile)
        regex_help = RegexHandler("^({})$".format(button_help["eng"]), self.help)
        # regex_deposit = RegexHandler("^({})$".format(button_deposit["eng"]), self.deposit)
        # regex_cashout = RegexHandler("^({})$".format(button_cashout["eng"]), self.cashout)
        # regex_help = RegexHandler("^({})$".format(button_help["eng"]), self.help)
        # regex_logout = RegexHandler("^({})$".format(button_logout["eng"]), self.logout)
        # regex_post_job = RegexHandler("^({})$".format(button_post_job["eng"]), self.post_job)
        # regex_pending_jobs = RegexHandler("^({})$".format(button_pending_jobs["eng"]), self.pending_jobs)


        # Conversation handlers
        conv_post_job = ConversationHandler(entry_points=[RegexHandler("^({})$".format(button_post_job["eng"]), self.post_job)],
            states={TITLE: [MessageHandler(Filters.text & ~Filters.command, self.job_title)],
                    DISCRIPTION: [MessageHandler(Filters.text & ~Filters.command, self.job_discription)],
            },
            fallbacks=[RegexHandler("^({})$".format("exit"), self.post_job_conv_end)]
        )

        # on noncommand i.e message - echo the message on Telegram
        message_contact = MessageHandler(Filters.contact, self.register)
        message_echo = MessageHandler(Filters.text & ~Filters.command, self.echo)
        



        # Add handlers to the dispatcher
        dispatcher.add_handler(conv_post_job)

        dispatcher.add_handler(command_start)

        dispatcher.add_handler(regex_register)
        dispatcher.add_handler(regex_login_freelancer)
        dispatcher.add_handler(regex_login_employer)
        dispatcher.add_handler(regex_profile)
        dispatcher.add_handler(regex_help)
        # dispatcher.add_handler(regex_deposit)
        # dispatcher.add_handler(regex_cashout)
        # dispatcher.add_handler(regex_logout)        
        # dispatcher.add_handler(regex_post_job)
        # dispatcher.add_handler(regex_pending_jobs)

        dispatcher.add_handler(message_contact)
        dispatcher.add_handler(message_echo)
        
        dispatcher.add_handler(CallbackQueryHandler(self.inline_button))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    
    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.
    def start(self, update: Update, context: CallbackContext) -> None:
        # Send a message when the command /start is issued
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        if not db.is_user_registered(chat_id):
            super().keyboard(update, context, text_register[lang], [[button_register[lang]]], True)
        else:
            # Check if the start link contains invite or additional data with it
            text = update.message.text[7:]
            if text != "":
                if re.match("^(jid[0-9]*)$", text):
                    job_id = int(text[3:])
                    formatted_text = fm.format_job(db.get_job_with_id(job_id))
                    super().show_message(update=update, context=context, text=formatted_text, parse=ParseMode.HTML)
                    # displays a job and asks for a proposal
                    self.get_job(job_id)
            else:
                self.login_menu(update, context)

    def echo(self, update: Update, context: CallbackContext) -> None:
        # Echo the user message
        print("in echo")
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        super().show_message(update, context, text_error[lang])
        
    def is_user_registered(self, update: Update, context: CallbackContext) -> None:
        # Check if the user is already registered 
        # if false, ask the users phone and register it to the db
        # if true, inform him that he is already registered
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        if not db.is_user_registered(chat_id):
            contact_keyboard = KeyboardButton(text=button_share_number[lang], request_contact=True)
            custom_keyboard = [[contact_keyboard]]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
            update.message.reply_text(text=text_share_number_req[lang], reply_markup=reply_markup)
        else:
            super().show_message(update, context, text_already_registered[lang])

    # Handles filter.contact messages and registers the user if not in already registered
    def register(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        if not db.is_user_registered(chat_id):
            phone = update.message.contact.phone_number
            first_name = update.message.from_user.first_name
            username = update.message.from_user.username

            if db.register(chat_id, phone, first_name, username):
                self.login_menu(update, context)
            else:
                super().show_message(update, context, text_error[lang])
                super().keyboard(update, context, text_register[lang], [[button_register[lang]]], True)
        else:
            super().show_message(update, context, text_already_registered[lang])

    # Displays the login menu
    def login_menu(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        super().keyboard(update, context, text_login[lang], [[button_login_freelancer[lang], button_login_employer[lang]]], True)

    # Displays the freelancer menu
    def freelancer_menu(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id) 
        menu = [[button_profile[lang],  button_deposit[lang]],[button_cashout[lang], button_help[lang]], [button_logout[lang]]]
        super().keyboard(update, context, text_welcome[lang], menu, False)

    # Displays the employer menu
    def employer_menu(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        menu = [[button_post_job[lang], button_jobs[lang]], [button_profile[lang], button_deposit[lang]], [button_help[lang], button_logout[lang]]]
        super().keyboard(update, context, text_welcome[lang], menu, False)
     
    # Get user profile from db if the user exists and format it 
    # then display the profile
    def profile(self, update: Update, context: CallbackContext) -> None:
        print("in profile")
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        data = db.get_profile(chat_id)
        # check if the user exists 
        if len(data) > 0:
            formatted_text = fm.format_profile(data)
            super().show_message(update=update, context=context, text=formatted_text, parse=ParseMode.HTML)
        else:
            super().show_message(update, context, text_error[lang])

    # Lets the user depost money using varios payment methods
    def deposit(self, update: Update, context: CallbackContext) -> None:
        pass
    
    # Lets the user cashout money using varios payment methods
    def cashout(self, update: Update, context: CallbackContext) -> None:
        pass

    # Displays a help information
    def help(self, update: Update, context: CallbackContext) -> None:
        print("in help")
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        super().show_message(update=update, context=context, text=text_help[lang], parse=ParseMode.HTML)

    def logout(self, update: Update, context: CallbackContext) -> None:
        self.login_menu(update, context)
    
    # Entery point for posting a job
    def post_job(self, update: Update, context: CallbackContext) -> int:
        # context.bot.sendMessage(chat_id=f"@{channel}", text=)
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        super().keyboard(update=update, context=context, text=text_job_title_req[lang], keyboard=[[button_main[lang]]], one_time=True)
        return TITLE

    # Ends conv between post job and the user
    def post_job_conv_end(self, update: Update, context: CallbackContext) -> int:
        self.employer_menu(update, context)
        return ConversationHandler.END

    # Asks the user for the job title, saves it to the database and continues to the discription
    def job_title(self, update: Update, context: CallbackContext) -> int:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        job_title = update.message.text
        if job_title != button_main[lang]:
            if db.add_job(chat_id, job_title):
                super().keyboard(update=update, context=context, text=text_job_discription_req[lang], keyboard=[[button_main[lang]]], one_time=True)
                return DISCRIPTION
            else:
                super().show_message(update, context, text_error[lang])
                self.employer_menu(update, context)
                return ConversationHandler.END
        else:
            self.employer_menu(update, context)
            return ConversationHandler.END
            

    # Asks the user for a discription and updates the job table at the database
    def job_discription(self, update: Update, context: CallbackContext) -> int:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        discription = update.message.text
        if discription != button_main[lang]:
            if db.add_job_discription(chat_id, discription):
                # Show message with inline keyboard to submit the job
                self.show_job(update, context)
                return ConversationHandler.END
            else:
                super().show_message(update, context, text_error[lang])
                self.employer_menu(update, context)
                return ConversationHandler.END
        else:
            self.employer_menu(update, context)
            return ConversationHandler.END

    def show_job(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        lang = self.get_lang(chat_id)
        data = db.get_job(chat_id)
        if len(data) > 0:
            job_id = data["job_id"]
            inline_keyboard = [[[button_edit[lang], button_edit[lang]], [button_submit[lang], f"jid{job_id}"]]]
            formatted_text = fm.format_job(data)
            # display the job for the user, and Give options to either edit or submit 
            super().inline_keyboard(update=update, context=context, text=formatted_text, keyboard=inline_keyboard, parse=ParseMode.HTML)

    def jobs(self, update: Update, context: CallbackContext) -> None:
        pass
    
    # Handles every callback data coming from the inline keyboard
    def inline_button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        chat_id = query.message.chat_id
        lang = self.get_lang(chat_id)
        text = query.data
        if re.match("^(jid[0-9]*)$", text):
            job_id = int(text[3:])
            data = db.get_job_with_id(job_id)
            formatted_text = fm.format_job(data)
            context.bot.sendMessage(chat_id=f"@{channel}", text=formatted_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Apply", url=f"https://t.me/{bot_username}?start={text}")]]))
    
    def get_job(self, job_id: int) -> None:
        pass

def main():
    # create freelance object with a bot_token and start it
    freelancebot = Freelance(bot_token)
    freelancebot.start_bot()

if __name__ == '__main__':
    main()