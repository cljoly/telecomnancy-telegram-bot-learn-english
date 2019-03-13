#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
from dbhelper import DBHelper
from random import randint
import os

import article

db = DBHelper()
db.setup()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Flags
requesting_english = False
testing_english = False
english_value = ''
requesting_french = False
testing_french = False
french_value = ''
score = 0

def reset_dict_flags():
    global requesting_english
    global testing_english
    global english_value
    global requesting_french
    global testing_french
    global french_value

    requesting_english = False
    testing_english = False
    english_value = ''
    requesting_french = False
    testing_french = False
    french_value = ''


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def dictAdd(bot, update):
    """"Prompts the user to add words to their dictionary when the command /dictAdd is issued"""
    update.message.reply_text('Please enter the english word, type \"\dictCancel\" to cancel')
    global requesting_english
    requesting_english = True


def dictAll(bot, update):
    """Prints all words known in the dictionnary"""
    items = db.get_dict()
    message = "\n".join(items)
    update.message.reply_text(message)


def dictCancel(bot, update):
    """Resets all flags and values for the dictionnary"""
    reset_dict_flags()


def dictTest(bot, update):
    """Tests the user on a word from their dictionnary"""
    entry_count = db.get_dict_entry_count()
    r = randint(1, entry_count)
    [french, english] = db.get_dict_entry(r)
    r = randint(0, 1)
    if r == 0:
        update.message.reply_text('Translate ' + english + ' in french')
        global testing_french
        testing_french = True
        global english_value
        english_value = english
    else:
        update.message.reply_text('Translate ' + french + ' in english')
        global testing_english
        testing_english = True
        global french_value
        french_value = french


def dictScore(bot, update):
	"""Returns user score"""
	global score
	update.message.reply_text('You scored '+str(score)+' points!')


def echo(bot, update):
    """Handles the user messages."""
    global requesting_english
    global testing_english
    global english_value
    global requesting_french
    global testing_french
    global french_value

    if (requesting_english == True):
        english_value = update.message.text
        update.message.reply_text('You typed: ' + english_value)
        update.message.reply_text('Please enter the french translation')
        requesting_english = False
        requesting_french = True
        return

    if (requesting_french == True):
        french_value = update.message.text
        update.message.reply_text('You typed: ' + french_value)
        db.add_item(french_value, english_value)
        update.message.reply_text('Entry has been added to database')
        reset_dict_flags()
        return

    if (testing_english == True):
        english_value = update.message.text
        update.message.reply_text('You typed: ' + english_value)
        if (english_value in db.get_english(french_value)):
            update.message.reply_text('Correct!')
        else:
            update.message.reply_text('Wrong!')
        reset_dict_flags()
        return

    if (testing_french == True):
        french_value = update.message.text
        update.message.reply_text('You typed: ' + french_value)
        if (french_value in db.get_english(english_value)):
            update.message.reply_text('Correct!')
            global score
            score += 1
        else:
            update.message.reply_text('Wrong!')
            reset_dict_flags()
        return


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def articleSelection(bot, update):
    sources = article.sources
    keyboard = [
        [InlineKeyboardButton("🗞️ " + news_name, callback_data=id)]
        for id, news_name in enumerate(sources.keys())
    ]
    keyboard.append([
        InlineKeyboardButton("👀 List", callback_data="-2"),
        InlineKeyboardButton("👌 All set", callback_data="-1")
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def articleCallback(bot, update):
    sources = article.sources
    query = update.callback_query
    source_number = int(query.data)
    print(query.data)
    t = "Callback: {}".format(source_number)
    print(t)
    if (source_number >= 0):
        news_source_name = list(sources.keys())[source_number]
        username = update.effective_user.username
        db.add_subscription(username, news_source_name)
        query.answer("You have subscribed to 🗞 {}".format(news_source_name))
    elif source_number == -1:
        query.edit_message_text(text="You will get your articles for lunch 🍽️. See you soon!")
    elif source_number == -2:
        # TODO List sources subscribed to
        query.edit_message_text(text="List")
    else:
        query.edit_message_text(text="Error")


def subscriptionsList(bot, update):
    """ List user subscription """
    username = update.effective_user.username
    subs = db.get_subscriptions(username)
    sources = article.sources
    keyboard = [
        [InlineKeyboardButton("🗞️ " + news_name, callback_data=id)]
        for id, news_name in enumerate(subs)
    ]
    keyboard.append([
        InlineKeyboardButton("👌 All set", callback_data="-1")
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("734595784:AAGLpr67me5zDP-wObrh3NY-KIA0JIXcKvA")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("dictAdd", dictAdd))
    dp.add_handler(CommandHandler("dictTest", dictTest))
    dp.add_handler(CommandHandler("dictCancel", dictCancel))
    dp.add_handler(CommandHandler("dictScore", dictScore))
    dp.add_handler(CommandHandler("select", articleSelection))
    dp.add_handler(CommandHandler("listSub", subscriptionsList))
    # dp.add_handler(CommandHandler("suggest", articleSuggestion))
    dp.add_handler(CallbackQueryHandler(articleCallback))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
