import os
import fcntl
import datetime
import time
import json
import glob
import calendar
import locale
import logging
from shutil import copyfile
from telegram import User

locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

FULL_PATH = os.path.dirname(os.path.realpath(__file__))
CONF_FOLDER = "conf"
DEFAULT_CONF_FILE = "conf.json"
EXT = ".json"
CHAT_TRASH_TEMPLATE = "chat_trash_{}.json"

# Logging
try:
    os.makedirs(os.path.join(FULL_PATH, "log"))
except FileExistsError:
    # directory already exists
    pass

log_file = os.path.join(FULL_PATH, "log", "noobot_trash.log")
logger = logging.getLogger("noobot_trash")
logging.basicConfig(filename=log_file,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

prefs_file = None
prefs = {}
g_chat_id = None

# Trash key
CALENDAR_KEY = "calendar"
TRASH_LIST_KEY = "trash-list"
TRASH_TURN_KEY = "trash-turn"
USERS = "users"
THROWED_KEY = "trash_threw"

limit_hour = 17


def adjust_time():
    # TODO: specificare da file di conf l'ora limite
    adjust = (1 if datetime.datetime.today().hour < limit_hour else 0)
    return (datetime.datetime.today().weekday() - adjust) % 7


# always call this to avoid KeyError exceptions
def trash_start(chat_id):
    global prefs_file
    global prefs
    global g_chat_id

    if g_chat_id != chat_id:
        logger.info("Loading chat_id {}".format(chat_id))
        prefs_file = os.path.join(CHAT_TRASH_TEMPLATE.format(chat_id))
        prefs = load_conf(prefs_file)  # create conf file if first rum fot chat_id
        g_chat_id = chat_id

        try:
            prefs[chat_id]
        except KeyError:
            logger.info("Creating chat_id {}".format(chat_id))
            prefs[chat_id] = {}
            prefs[chat_id][CALENDAR_KEY] = {"0": "",
                                            "1": "",
                                            "2": "",
                                            "3": "",
                                            "4": "",
                                            "5": "",
                                            "6": ""}
            prefs[chat_id][TRASH_LIST_KEY] = []
            prefs[chat_id][TRASH_TURN_KEY] = []
            prefs[chat_id][USERS] = {}
            prefs[chat_id][THROWED_KEY] = -1


def user_add(chat_id, user):
    """
    Add an user
    :param chat_id: ( string ) telegram.Chat.id
    :param user: ( telegram.User ) [(http://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html)]
    :return: True - user added/updated
    :return: False - user already known
    """
    if user.is_bot:
        return False

    global prefs
    trash_start(chat_id)
    uid = str(user.id)
    local_user = user_get(chat_id, uid)
    update = False

    if local_user is None:
        update = True
    elif local_user.name != user.name or local_user.first_name != user.first_name:
        update = True
    elif local_user.is_delete:
        update = True

    if update:
        user.is_delete = False
        prefs[chat_id][USERS][uid] = user.to_dict()
        to_store()

    return update


def user_get(chat_id, uid):
    """
    Return the user (telegram.User)
    :param chat_id: ( string ) telegram.Chat.id
    :param uid: ( int or string ) id of user to get
    :return: User ( telegram.User ) [(http://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html)]
    :return: None
    """
    trash_start(chat_id)
    try:
        user = User.de_json(prefs[chat_id][USERS][str(uid)], None)
        try:
            user.is_delete = prefs[chat_id][USERS][str(uid)]["is_delete"]
        except KeyError:
            user.is_delete = False
        return user
    except KeyError:
        return None


def user_delete(chat_id, user):
    """
    Delete the user from the list
    :param chat_id: ( string ) telegram.Chat.id
    :param user: ( telegram.User ) [(http://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html)]
    :return: True - user deleted
    :return: False - user not deleted
    """
    if user.is_bot:
        return False
    local_user = user_get(chat_id, user.id)
    if local_user is None:
        return False
    if local_user.is_delete:
        return False

    global prefs
    trash_start(chat_id)
    prefs[chat_id][TRASH_TURN_KEY][:] = [u for u in prefs[chat_id][TRASH_TURN_KEY] if u.get('id') != user.id]
    prefs[chat_id][USERS][str(user.id)]["is_delete"] = True
    # prefs[chat_id][TRASH_LIST_KEY][:] = [u for u in prefs[chat_id][TRASH_TURN_KEY] if u.get('id') != user.id]
    # del(prefs[chat_id][USERS][str(user.id)])
    to_store()
    return True


def user_is_delete(chat_id, uid):
    """
    Tell if the user uid is deleted
    :param chat_id: ( string ) telegram.Chat.id
    :param uid: ( int or string ) id of user to get
    :return: True user is deleted
    :return: False otherwise
    """
    trash_start(chat_id)
    return True if user_get(chat_id, uid).is_delete else False


def user_total(chat_id):
    """
    DO NOT USE
    :param chat_id:
    :return:
    """
    global prefs
    trash_start(chat_id)
    return len(prefs[chat_id][USERS])


def trash_throw(chat_id, user):
    """
    Set which user in which chat thrown the trash
    :param chat_id: ( string ) telegram.Chat.id
    :param user: ( telegram.User ) [(http://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html)]
    :return: False: trash already thrown
    :return: True: otherwise
    """
    global prefs
    trash_start(chat_id)

    # aggiunge o aggiorna l'user se è modificato
    user_add(chat_id, user)

    if trash_thrown(chat_id):
        return False
    else:
        # if user.id != turn_get_user(chat_id).id:
        #     pass

        ts = int(time.time())
        u = {'id': user.id, 'time': ts}

        # update trash-list
        # remember only last x entry and append the user
        if len(prefs[chat_id][TRASH_LIST_KEY]) >= 4:
            # no exceptions raised
            prefs[chat_id][TRASH_LIST_KEY].pop(0)
        prefs[chat_id][TRASH_LIST_KEY].append(u)

        # update trash-turn
        prefs[chat_id][TRASH_TURN_KEY][:] = [u for u in prefs[chat_id][TRASH_TURN_KEY] if u.get('id') != user.id]
        prefs[chat_id][TRASH_TURN_KEY].append(u)

        trash_thrown(chat_id, s=True)
        return True


def trash_set_calendar(chat_id, cal):
    """
    Set munnezza calendar ## TODO: inline telegram command
    :param chat_id: ( string ) telegram.Chat.id
    :param cal: ( dict ) { 'Monday': 'string', 'Tuesday': 'string', ... }
    :return: True: ok
    :return:False: some error
    """
    pass


def trash_get_calendar(chat_id):
    """
    Get the calendar
    :param chat_id: ( string ) telegram.Chat.id
    :return: ( dict ) { 'Monday': 'string', 'Tuesday': 'string', ... }
    """
    global prefs
    trash_start(chat_id)
    cal = [None] * 7
    for item in prefs[chat_id][CALENDAR_KEY]:
        item = int(item)
        cal[item] = {"day": calendar.day_name[item], "string": prefs[chat_id][CALENDAR_KEY][str(item)]}
        # cal.insert(item, {calendar.day_name[item]: prefs[chat_id][CALENDAR_KEY][str(item)]})
    return cal


def trash_get_calendar_day(chat_id):
    """
    Get what to throw today

    :param chat_id: (string) telegram.Chat.id
    :return: string
    """
    global prefs
    trash_start(chat_id)
    t = adjust_time()
    if not prefs[chat_id][CALENDAR_KEY]:
        cal = None
    else:
        try:
            cal = prefs[chat_id][CALENDAR_KEY][str(t)]
        except KeyError:
            cal = None
    return cal


def trash_get_user_turn(chat_id):
    """
    Get user turn
    :param chat_id: (string) telegram.Chat.id
    :return: user (telegram.User)
    """
    global prefs
    trash_start(chat_id)
    try:
        user_id = str(prefs[chat_id][TRASH_TURN_KEY][0]['id'])
        user = user_get(chat_id, user_id)
    except (KeyError, IndexError):
        user = None

    return user


def trash_get_user_thrown(chat_id):
    trash_start(chat_id)
    try:
        if len(prefs[chat_id][TRASH_TURN_KEY]) == 0:
            return None
    except KeyError:
        return None
    user_list = []
    for line in prefs[chat_id][TRASH_TURN_KEY]:
        user = user_get(chat_id, line['id'])
        user.time = line['time']
        user_list.append(user)
    return user_list

def turn_push():
    """
    Get a list of chat to push info
    :return: [{"chat": c, "user": user, "cal": cal}]
    """
    chats_path = os.path.join(FULL_PATH, CONF_FOLDER)
    chat_ids = glob.glob(chats_path + "/" + CHAT_TRASH_TEMPLATE.format("*"))
    print(chat_ids)
    chat_ids = [os.path.basename(c)[11:].replace(".json", "") for c in chat_ids]
    print(chat_ids)
    to_push = []
    for c in chat_ids:
        print(c, trash_thrown(c))
        if trash_thrown(c):
            continue
        user = trash_get_user_turn(c)
        cal = trash_get_calendar_day(c)
        print("User", user, "calendar", cal)
        if cal is None or cal == "":
            continue
        to_push.append({"chat": c, "user": user, "cal": cal})
    print(to_push)
    return to_push


def trash_get_user_list(chat_id):
    """
    Get the list of last user
    :param chat_id: (string) telegram.Chat.id
    :return: list of user (telegram.User)
    """
    last_x = 3
    trash_start(chat_id)
    try:
        if len(prefs[chat_id][TRASH_LIST_KEY]) == 0:
            return None
    except KeyError:
        return None
    user_list = []
    for line in prefs[chat_id][TRASH_LIST_KEY][-last_x:]:
        user = user_get(chat_id, line['id'])
        user.time = line['time']
        user_list.append(user)
    return user_list


def trash_thrown(chat_id, s=False):
    """
    Check or set if trash was thrown
    :param chat_id: (string) telegram.Chat.id
    :param s: ( boolean ) True to store
    :return: True - Trash already throwed
    :return: False - otherwise
    """
    global prefs
    trash_start(chat_id)
    t = adjust_time()
    throw = (False if prefs[chat_id][THROWED_KEY] != t else True)
    # throw = False  # for testing
    if s:
        prefs[chat_id][THROWED_KEY] = t
        to_store()
    return throw


def trash_undo_last_change(chat_id):
    """

    :param chat_id:
    :return:
    """
    trash_start(chat_id)
    full_file = os.path.join(FULL_PATH, CONF_FOLDER, CHAT_TRASH_TEMPLATE.format(chat_id))
    copyfile(full_file + ".1", full_file)


###########################
### Store backend start ###
###########################


def load_conf(file=DEFAULT_CONF_FILE):
    """
    Load conf from file
    :param file: ( string ) File path relative to this file
    :return: json
    """
    full_file = os.path.join(FULL_PATH, CONF_FOLDER, file)
    try:
        f = open(full_file, 'r')
    except IOError:
        # file doesn't exist, create it and return empty conf
        f = open(full_file, 'w')
        f.close()
        return {}

    fcntl.flock(f, fcntl.LOCK_EX)
    conf = json.load(f)
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()
    return conf


def store_conf(file=DEFAULT_CONF_FILE, j="", backup=False):
    """
    Save to file
    :param file: ( string ) File path relative to this file
    :param j: json
    :param backup: True/False make a backup
    :return:
    """
    full_file = os.path.join(FULL_PATH, CONF_FOLDER, file)
    # crea una copia di backup
    if backup:
        copyfile(full_file, full_file + ".1")
    with open(full_file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        json.dump(j, f, indent=2)
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def to_store():
    """
    Save the current json in the current prefs_file
    :return:
    """
    global prefs_file
    global prefs
    store_conf(prefs_file, prefs, True)

###########################
#### Store backend end ####
###########################
