#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from telegram import KeyboardButton, InlineKeyboardMarkup

import noobot_trash_backend_json as backend


# Help
def help_me(update, context):
    string = """Ciao sono il NooBot!
    Easy peasy lemon squeezy: TODO ora non mi vaaaaa! 
    Comunque i comandi sono i seguenti:
    /me - sono stato io!!1
    /rip - Noo non ci sono
    /nope - Busta mezza piena!?

    /turn - cosa?! chi?!
    /history - chi!? quando?!
    /calendar - calendario della munnezza
    /set - imposa il calendario della munnezza
    /help - Aiuto
    """
    print("Help:chat_id", update.message.chat_id)
    context.bot.send_message(chat_id=str(update.message.chat_id), text=string)


# ## Gestione utenti ###
def start_user(update, context):
    """
    Inizzializza un user al BOT
    """
    chat_id = str(update.message.chat_id)
    user = update.message.from_user
    string = ("aggiunto/aggiornato" if backend.user_add(chat_id, user) else "ti conosco già ; )")
    context.bot.send_message(chat_id=chat_id, text="{} {}".format(user.name, string))


def add_member(update, context):
    """
    aggiunge user al bot (quando viene aggiuto al gruppo)
    """
    chat_id = str(update.message.chat_id)
    users = update.message['new_chat_members']
    string = ""
    for user in users:
        if backend.user_add(chat_id, user):
            string += "{} ".format(user.name)
    if string != "":
        context.bot.send_message(chat_id=chat_id, text="Aggiunti: {}".format(string))


def delete_me(update, context):
    """
    cancella user dal bot
    """
    chat_id = str(update.message.chat_id)
    user = update.message.from_user
    backend.user_delete(chat_id, user)
    context.bot.send_message(chat_id=chat_id, text="Ciao ciao {} :'(".format(user.name))


def remove_member(update, context):
    """
    rimuove user al bot (quando viene rimosso dal gruppo)
    """
    chat_id = str(update.message.chat_id)
    user = update.message['left_chat_member']
    if backend.user_delete(chat_id, user):
        context.bot.send_message(chat_id=chat_id, text="Ciao ciao {}".format(user.name))


# ## Gestione Munnezza ###
def me(update, context):
    """
    Notifica chi ha buttata la munnezza
    """
    chat_id = str(update.message.chat_id)
    user = update.message.from_user
    string = ("scesa da " + user.name if backend.trash_throw(chat_id, user) else "già scesa!!!")

    context.bot.send_message(chat_id=chat_id, text="Munnezza {}".format(string))


def nope(update, context):
    """
    Notifica che la munnezza non si deve buttare
    """
    chat_id = str(update.message.chat_id)
    if backend.trash_get_calendar_day(chat_id).find("Umido") != -1:
        string = "\ud83e\udd22!! NOPE"
    else:
        string = ("Bravo!!1 No allo spreco." if not backend.trash_thrown(chat_id) else "Munnezza già scesa")
        backend.trash_thrown(chat_id, True)
    context.bot.send_message(chat_id=chat_id, text=string)


def _turn(chat_id):
    """
    A chi tocca buttare la munnezza
    """
    chat_id = str(chat_id)
    string = "idk!"
    # print("fun::turn::thrown::{}".format(thrown(chat_id)))
    # if trash_thrown(chat_id):
    #    string = "Munnezza già scesa"
    # else:
    #    user = trash_get_user_turn(chat_id)
    #    if user is not None:
    #        string = "Tocca a: {}".format(user.name)

    user = backend.trash_get_user_turn(chat_id)
    if user is not None:
        string = "Tocca a: {}".format(user.name)

    # bot.send_message(chat_id=chat_id, text=string)
    return string


def _trash(chat_id):
    """
    """
    chat_id = str(chat_id)
    cal = backend.trash_get_calendar_day(chat_id)
    # print("fun::trash::get_day::{}".format(thrown(cal)))
    if cal is None:
        string = "Impostare il calendario"
    elif cal == "":
        string = "Nulla da scendere. Party time!!1"
    else:
        string = "Munnezza già scesa!!!" if backend.trash_thrown(chat_id) else "Scendere: {}".format(cal)

    # bot.send_message(chat_id=chat_id, text=string)
    return string


def turn_trash(update, context):
    print("update:", update)
    print("context", context)
    chat_id = update.message.chat.id
    print(chat_id)
    turn_msg = _turn(chat_id)
    trash_msg = _trash(chat_id)
    # msg = "{}\n{}".format(trash_msg, turn_msg)
    msg = f"{trash_msg}\n{turn_msg}\n/me -> Sono stato io\n\n/rip -> Noo non ci sono\n\n/nope -> Busta mezza piena!?"
    _send_msg(context.bot, update, msg)
    return


def user_list(update, context):
    """
    Lista di chi ha buttato la munnezza
    """
    chat_id = str(update.message.chat_id)
    u_l = backend.trash_get_user_list(chat_id)
    string = "Sicuri siete puliti? Nessuno ha buttato la munnezza"
    if u_l is not None:
        string = ""
        for u in u_l:
            string += "{} da {}\n" \
                .format(datetime.datetime.fromtimestamp(int(u.time)).strftime('%d %b alle %H:%M'),
                        ("Utente cancellato" if u.is_delete else u.first_name))

    context.bot.send_message(chat_id=chat_id, text=string)


def set_day(day):
    pass


def set_type(type):
    pass


# ## Gestione calendario ###
def set_calendar(update, context):
    """
    Imposta il calendario
    """
    print(update.message.message_id)

    if len(context.args) == 0:
        week_day = [['Lun', 'Mar', 'Mer'],
                    ['Gio', 'Ven', 'Sab', 'Dom']]

        button_list = [[KeyboardButton(s)] for s in week_day]

        reply_markup = InlineKeyboardMarkup(button_list)
        context.bot.send_message(chat_id=str(update.message.chat_id),
                                 text="Giorno della settimana",
                                 reply_markup=reply_markup)
    context.bot.send_message(chat_id=str(update.message.chat_id), text="TODO! sory sory!")


def get_calendar(update, context):
    """
    Visualizza il calendario
    """
    chat_id = str(update.message.chat_id)
    cal_list = backend.trash_get_calendar(chat_id)

    if len(cal_list) > 0:
        msg = "Calendario:\n"
        for item in cal_list:
            if item["string"] == "" or item["string"] is None:
                continue
            msg += "{}:\t{}\n".format(item["day"], item["string"])
    else:
        msg = "Impostare il calendario!"

    context.bot.send_message(chat_id=chat_id, text="{}".format(msg))


def trash_push(context):
    """
    Notifica nelle chat il turno
    """
    la_lista = backend.turn_push()
    print(la_lista)
    # print(la_lista)
    for chat_to_push in la_lista:
        # print("chat: {} - user {} - cal {}".format(chat_to_push["chat"], chat_to_push["user"], chat_to_push["cal"]))
        try:
            turn_msg = _turn(chat_to_push["chat"])
            trash_msg = _trash(chat_to_push["chat"])
            # msg = "{}\n{}".format(trash_msg, turn_msg)
            # TODO: ripristinare comando con i comandi
            msg = f"{trash_msg}\n{turn_msg}\n/me -> Sono stato io\n\n/rip -> Noo non ci sono\n\n/nope -> Busta mezza piena!?"
            context.bot.send_message(chat_id=chat_to_push["chat"],
                                     text=msg)
        except Exception as e:
            backend.logger.info(e)


def rip(update, context):
    chat_id = str(update.message.chat_id)
    users = backend.trash_get_user_thrown(chat_id)
    user_msg = update.message.from_user
    idx = users.index(user_msg)
    try:
        user = users[idx + 1]
        try:
            username = user.username
            msg = "\ud83d\udc80 @{} \ud83d\udc80".format(username)
        except KeyError:
            username = user.first_name
            msg = "\ud83d\udc80 {} \ud83d\udc80".format(username)
    except Exception:
        msg = "\ud83d\udc80\u2620\ufe0f\ud83d\udc80"
    _send_msg(context.bot, update, msg)


def _send_msg(bot, update, msg):
    bot.send_message(chat_id=str(update.message.chat_id), text="{}".format(msg))


# test command
def undo(bot, update):
    chat_id = str(update.message.chat_id)
    backend.trash_undo_last_change(chat_id)
    bot.send_message(chat_id=str(update.message.chat_id), text="Undo on {}".format(chat_id))


def _list_admin_ids(bot, chat_id):
    # TODO: check qui reise exception
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
