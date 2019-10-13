import logging
import os
import os.path
import random
import telebot
import time
import urllib.request

import config

from collections import defaultdict
from enum import Enum
from utils import get_files_from_link as parse
from compressor.compress import unite_files as compress
from compressor.decompress import decompress_bytes as decompress


logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)

logger = logging.getLogger(__name__)


class Mode(Enum):
    NONE = 0
    COMPRESS = 1
    DECOMPRESS = 2
    LINK = 3
    ECHO = 4


class ChatData:
    def __init__(self):
        self.names_list = []
        self.data_list = []

    def clear(self):
        self.names_list.clear()
        self.data_list.clear()


bot_mode = Mode.NONE
chats_data = defaultdict(ChatData)


bot = telebot.TeleBot(config.token)


def get_files(prefix):
    all_files = os.listdir(".")
    return list(filter(lambda s: s.startswith(prefix), all_files))


def get_files_by_time(l_time, r_time):
    all_files = os.listdir(".")
    return list(
        filter(lambda s: l_time < os.path.getmtime(s) < r_time,
               all_files))


def compress_users_files(bot, message):
    chat_id = message.chat.id
    cur_chat = chats_data[chat_id]
    get_int = random.randint(100, 999)
    result_filename = ".interesting_box{}{}.jp".format(chat_id, get_int)
    compress(cur_chat.names_list, cur_chat.data_list, result_filename)
    cur_chat.clear()
    with open(result_filename, "rb") as comp:
        bot.send_document(chat_id, comp)
    os.remove(result_filename)
    bot.send_message(chat_id, "Here is compressed file.")


# /help, /start commands
@bot.message_handler(commands=["help", "start"])
def handle_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, config.help_text)


# /compress command
@bot.message_handler(commands=["compress"])
def handle_compress(message):
    """ Handle compress command """
    global bot_mode
    chat_id = message.chat.id
    if bot_mode is not Mode.COMPRESS:

        bot_mode = Mode.COMPRESS
        bot.send_message(chat_id, "Please, load files to compress.")

    else:
        bot_mode = Mode.NONE
        if chat_id not in chats_data:
            bot.send_message(chat_id, "Nothing to compress!")
            return

        compress_users_files(bot, message)


# /clink command
@bot.message_handler(commands=["clink"])
def handle_link(message):
    global bot_mode
    bot_mode = Mode.LINK
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please, type url.")


# /decompress command
@bot.message_handler(commands=["decompress"])
def handle_decompress(message):
    """ Handle decompress command """
    global bot_mode
    chat_id = message.chat.id
    if bot_mode is not Mode.DECOMPRESS:

        bot_mode = Mode.DECOMPRESS
        bot.send_message(
            chat_id,
            "Please, load compressed file to decompress."
        )

    else:
        bot_mode = Mode.NONE


# document handling
@bot.message_handler(
    # func=lambda message: message.document.mime_type == 'text/plain',
    content_types=['document']
)
def handle_file(message):
    global bot_mode
    chat_id = message.chat.id
    if bot_mode is Mode.COMPRESS:

        file_obj = bot.get_file(message.document.file_id)
        filename = message.document.file_name

        url = "https://api.telegram.org/file/bot{}/{}"
        url = url.format(config.token, file_obj.file_path)
        response = urllib.request.urlopen(url)

        data = response.read()
        chats_data[chat_id].data_list.append(data)
        chats_data[chat_id].names_list.append(filename)

        bot.send_message(
            message.chat.id,
            "File {} was eaten".format(filename)
        )
        logger.info("File {} to add compressor".format(filename))

    elif bot_mode is Mode.DECOMPRESS:
        logger.info("Decompress file section:.")
        bot_mode = Mode.NONE
        compressed_obj = bot.get_file(message.document.file_id)
        filename = message.document.file_name

        url = "https://api.telegram.org/file/bot{}/{}"
        url = url.format(config.token, compressed_obj.file_path)
        response = urllib.request.urlopen(url)

        data = response.read()
        logger.info("Data to decompress was recieved. Starting decompression.")
        left_time = time.time()
        decompress(data)
        right_time = time.time()
        logger.info("Decompression ended.")
        filenames_to_send = get_files_by_time(left_time, right_time)
        for current_filename in filenames_to_send:
            with open(current_filename, "rb") as file:
                bot.send_document(message.chat.id, file)
            os.remove(current_filename)

        bot.send_message(chat_id, "This files are in {}.".format(filename))
        logger.info("End decompression.")
    else:
        bot.send_message(chat_id, config.help_text)


@bot.message_handler()
def other_handler(message):
    global bot_mode
    ci = message.chat.id
    if bot_mode == Mode.LINK:
        bot_mode = Mode.NONE
        link = message.text
        chats_data[ci].clear()
        num, chats_data[ci].names_list, chats_data[ci].data_list = parse(link)
        if num == -1:
            bot.send_message(ci, "Invalid url!")
        elif num == 0:
            bot.send_message(ci, "Nothing to compress!")
        else:
            bot.send_message(ci, "Eaten {} files".format(num))
        compress_users_files(bot, message)
    else:
        bot.send_message(ci, "Type /help to see bot information.")


if __name__ == '__main__':
    bot.polling(none_stop=True)
