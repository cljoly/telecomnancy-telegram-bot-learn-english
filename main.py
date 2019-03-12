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
    t="Callback: {}".format(source_number)
    print(t)
    if (source_number>=0):
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
		db.add_item("french", "english")

def dictAll(bot, update):
		"""Prints all words known in the dictionnary"""
		items = db.get_items()
		message = "\n".join(items)
		update.message.reply_text(message)

def dictTest(bot, update):
		"""Tests the user on a word from their dictionnary"""
		r = randint(0,1);
		if r == 0:
				english = "english"
				french = db.get_french(english)
				update.message.reply_text('Translate'+english+'in french')
		else:
				french = "french"
				english = db.get_english(french)
				update.message.reply_text('Translate'+french+'in english')
				

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("778329810:AAElGVRiP4_tZCJvAE025qZ1ySTgBOAze80")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("dictAdd", dictAdd))
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
