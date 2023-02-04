#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from noobot_trash_command import *
from noobot_trash_command import _list_admin_ids


# Suppress error in log
def error_callback(update, context):
    backend.logger.warning('Update "%s" caused error "%s"', update, context.error)
    try:
        raise context.error
    except Exception:
        pass


# load conf file
conf = backend.load_conf("conf.json")
telegram_token = conf['telegram_noobot_trash_bot']['token']

updater = Updater(telegram_token)
dispatcher = updater.dispatcher
dispatcher.add_error_handler(error_callback)


# testing fun
def id(update, context):
    chat_id = str(update.message.chat_id)
    if update.message.from_user.id in _list_admin_ids(context.bot, chat_id):
        context.bot.send_message(chat_id=str(update.message.chat_id),
                                 text="{}".format(str(update.message.chat_id)))
    else:
        context.bot.send_message(chat_id=str(update.message.chat_id),
                                 text="{}".format("Volevi!"))


# testing command
dispatcher.add_handler(CommandHandler('id', id))

# Trash Bot Command
dispatcher.add_handler(CommandHandler('help', help_me))
dispatcher.add_handler(CommandHandler('start', start_user))

dispatcher.add_handler(CommandHandler('me', me))
dispatcher.add_handler(CommandHandler('nope', nope))
dispatcher.add_handler(CommandHandler('rip', rip))

dispatcher.add_handler(CommandHandler('turn', turn_trash))
dispatcher.add_handler(CommandHandler('history', user_list))

dispatcher.add_handler(CommandHandler('set', set_calendar, pass_args=True))
dispatcher.add_handler(CommandHandler('calendar', get_calendar))
dispatcher.add_handler(CommandHandler('delete_me', delete_me))
# Test command
# dispatcher.add_handler(CommandHandler('pushtest', trash_push))
# dispatcher.add_handler(CommandHandler('undo', undo))
# Add Message handler
# all'aggiunta di uno o più utenti restituisce una lista di telegram.User
# dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, add_member))
# quando si rimuove un utente
# dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, remove_member))
# cronjob
# TODO: tzname for DST
# DST Time "ora legale"
# updater.job_queue.run_daily(trash_push, datetime.time(19, 00, 00))
# updater.job_queue.run_daily(trash_push, datetime.time(22, 00, 00))
# NO DST Time "ora solare"
updater.job_queue.run_daily(trash_push, datetime.time(20, 30, 00))
# updater.job_queue.run_daily(trash_push, datetime.time(23, 30, 00))

# updater.job_queue.run_daily(push_turn, datetime.time(10,30,00), days=(1,1))
backend.logger.info("STARTING TRASH BOT...")
updater.start_polling()
updater.idle()
