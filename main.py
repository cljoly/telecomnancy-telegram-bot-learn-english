#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
from dbhelper import DBHelper
from random import randint
from random import shuffle
import os

import article

db = DBHelper()
db.setup()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Messages
article_lunch = "You will get your articles for lunch 🍽️. See you soon!"

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

    if update.message:
        update.message.reply_text(
            'Please tap on buttons to subscribe to a news source.\nTap another time to unsubscribe.',
            reply_markup=reply_markup)
    else:
        query = update.callback_query
        query.edit_message_text(text='Please tap on buttons to subscribe to a news source.\nTap another time to unsubscribe.',
                                reply_markup=reply_markup)


def articleCallback(bot, update):
    """ Callback for all articles """
    sources = article.sources
    query = update.callback_query
    source_number = int(query.data)
    print(query.data)
    t = "Callback: {}".format(source_number)
    print(t)
    username = update.effective_user.username
    if (source_number >= 0):
        news_source_name = list(sources.keys())[source_number]
        if article.toggle_subscription(db, username, news_source_name):
            query.answer("You have subscribed to 🗞 {}".format(news_source_name))
        else:
            query.answer("You have unsubscribed from 🗞 {}".format(news_source_name))

    elif source_number == -1:  # All set
        query.edit_message_text(text=article_lunch)
    elif source_number == -2:  # List subscription
        query.edit_message_text(text=genSubscriptionsMessage(username))
    elif source_number == -3:  # Article read, add word
        # TODO Call function to add words
        # reset_dict_flag()
        dictAdd(bot, update)

    # TestEasy
    elif source_number == -100:
        global score
        score += 1
        query.edit_message_text(text='You got it right!')
    elif source_number == -101:
        query.edit_message_text(text='Wrong!')

    # menu
    elif source_number == -1000: #articles
        articleSelection(bot, update)
    elif source_number == -1001: #add words
        dictAdd(bot, update)
    elif source_number == -1002: #easy
        dictTest2(bot, update)
    elif source_number == -1003: #hard
        dictTest(bot, update)
    elif source_number == -1004: #score
        dictScore(bot, update)
    else:
        query.edit_message_text(text="Error")


def genSubscriptionsMessage(username):
    subs = db.get_subscriptions(username)
    msgs = ["You have subscribed to:"]
    msgs += ["🗞️ " + news_name for news_name in subs]
    msgs += [article_lunch]
    return "\n".join(msgs)


def subscriptionsList(bot, update):
    """ List user subscription """
    username = update.effective_user.username
    msg = genSubscriptionsMessage(username)
    print("subs list", msg)
    update.message.reply_text(msg)


def articleSuggestion(bot, update):
    username = update.effective_user.username
    title, link = article.random_from_subscribed(db, username, )
    msg = "📰 {}\n🔗 {}".format(title, link)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✔️ Read, add words", callback_data=-3)]
    ])
    update.message.reply_text(msg, reply_markup=reply_markup)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi, I’m your new British friend and I would love to share my favorite articles with you. Here is a couple of media I find interesting. Tell me which one you would like to subscribe to and I will send you the latest articles daily.')
    articleSelection(bot, update)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def dictAdd(bot, update):
    """"Prompts the user to add words to their dictionary when the command /dictAdd is issued"""
    if update.message:
        update.message.reply_text('Please enter the english word, type \"/dictCancel\" to cancel')
    else:
        query = update.callback_query
        query.edit_message_text('Please enter the english word, type \"/dictCancel\" to cancel')
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
        if update.message:
            update.message.reply_text('Translate ' + english + ' in french, type \"/dictCancel\" to cancel')
        else:
            query = update.callback_query
            query.edit_message_text(
                text='Translate ' + english + ' in french, type \"/dictCancel\" to cancel')
        global testing_french
        testing_french = True
        global english_value
        english_value = english
    else:
        if update.message:
            update.message.reply_text('Translate ' + french + ' in english, type \"/dictCancel\" to cancel')
        else:
            query = update.callback_query
            query.edit_message_text(
                text='Translate ' + french + ' in english, type \"/dictCancel\" to cancel')
        global testing_english
        testing_english = True
        global french_value
        french_value = french


def dictTest2(bot, update):
    entry_count = db.get_dict_entry_count()
    r = randint(1, entry_count)
    r2 = r
    r3 = r

    if entry_count > 1:
        while r2 == r:
            r2 = randint(1, entry_count)
    if entry_count > 2:
        while r3 in [r, r2]:
            r3 = randint(1, entry_count)
    [french, english] = db.get_dict_entry(r)
    [french2, english2] = db.get_dict_entry(r2)
    [french3, english3] = db.get_dict_entry(r3)

    r = randint(0, 1)
    keyboard = []
    if r == 0:
        keyboard.append([
            InlineKeyboardButton(french, callback_data="-100"),
            InlineKeyboardButton(french2, callback_data="-101"),
            InlineKeyboardButton(french3, callback_data="-101")
        ])
        translate_to = "english 🇬🇧"  # 🇺🇸
        translating = english
    else:
        keyboard.append([
            InlineKeyboardButton(english, callback_data="-100"),
            InlineKeyboardButton(english2, callback_data="-101"),
            InlineKeyboardButton(english3, callback_data="-101")
        ])
        translate_to = "french 🇫🇷"
        translating = french
    shuffle(keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text("click on the correct " + translate_to + " translation for the word \"" + translating+"\"", reply_markup=reply_markup)
    else:
        query = update.callback_query
        query.edit_message_text(
            text="click on the correct " + translate_to + " translation for the word \"" + translating+"\"",
            reply_markup=reply_markup)


def dictScore(bot, update):
    """Returns user score"""
    global score

    if update.message:
        update.message.reply_text('You scored ' + str(score) + ' point(s)')
        if score < 10:
            update.message.reply_text('Try to go for 10 points today!')
        else:
            update.message.reply_text('Good job!  💯')
    else:
        query = update.callback_query
        if score < 10:
            query.edit_message_text(text='You scored ' + str(score) + ' point(s) \n Try to go for 10 points today!')
        else:
            query.edit_message_text(text='You scored ' + str(score) + ' point(s) \n Good job!  💯')


def echo(bot, update):
    """Handles the user messages."""
    global requesting_english
    global testing_english
    global english_value
    global requesting_french
    global testing_french
    global french_value
    global score

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
            score += 3
        else:
            update.message.reply_text('Wrong!')
        reset_dict_flags()
        return

    if (testing_french == True):
        french_value = update.message.text
        update.message.reply_text('You typed: ' + french_value)
        if (french_value in db.get_french(english_value)):
            update.message.reply_text('Correct!')
            score += 3
        else:
            update.message.reply_text('Wrong!')
            reset_dict_flags()
        return


def mainMenu(bot, update):
    """Shows a menu from which the user can do the most common actions"""
    keyboard = [
        [InlineKeyboardButton("Manage subscriptions", callback_data="-1000")],
        [InlineKeyboardButton("Add a word to the database", callback_data="-1001")],
        [InlineKeyboardButton("Play an easy game to earn points", callback_data="-1002")],
        [InlineKeyboardButton("Play a harder game to earn points", callback_data="-1003")],
        [InlineKeyboardButton("See your score", callback_data="-1004")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Select an option to launch the associated command",
        reply_markup=reply_markup)


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
    dp.add_handler(CommandHandler("dictTest", dictTest))
    dp.add_handler(CommandHandler("dictTest2", dictTest2))
    dp.add_handler(CommandHandler("dictCancel", dictCancel))
    dp.add_handler(CommandHandler("dictScore", dictScore))
    dp.add_handler(CommandHandler("select", articleSelection))
    dp.add_handler(CommandHandler("list", subscriptionsList))
    dp.add_handler(CommandHandler("suggest", articleSuggestion))
    dp.add_handler(CommandHandler("menu", mainMenu))

    # QueryHandler
    dp.add_handler(CallbackQueryHandler(articleCallback))

    # on noncommand
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
