import random

from telegram import Updater, Bot, Update
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

from definitions import definitions
from bot_token import token

points_per_answer = 1
questions_per_user = 10

keyboard = [["1", "2", "3"]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

updater = Updater(token=token)
dispatcher = updater.dispatcher

chats = {}
all_words = list(definitions.keys())


def start(bot, update):
    """
    Handles /start command

    :type update: Update
    :type bot: Bot
    :returns None
    """
    chat_id = update.message.chat_id
    if chat_id in chats:
        bot.sendMessage(chat_id, "Ты уже начал игру. Отвечай на вопрос", reply_markup=reply_markup)
    else:
        start_game(bot, chat_id)


def start_game(bot, chat_id):
    random.shuffle(all_words)
    chats[chat_id] = {"index": 0,
                      "words": all_words[:questions_per_user],
                      "points": 0}
    bot.sendMessage(chat_id=chat_id, text='Привет! Я простой бот, который умеет играть в "Завалинку"')
    bot.sendMessage(chat_id=chat_id,
                    text='Всего вопросов будет {0}. '
                         'Ты можешь в любой момент закончить игру командой /stop'.format(questions_per_user))
    bot.sendMessage(chat_id=chat_id, text='Давай я задам тебе первый вопрос')
    send_question(bot, chat_id)


def stop(bot, update):
    """
    Handles /stop command

    :type update: Update
    :type bot: Bot
    """
    chat_id = update.message.chat_id
    if chat_id not in chats:
        send_start_game(bot, chat_id)
    else:
        bot.sendMessage(chat_id, "Жаль, что не доиграли.")
        stop_game(bot, chat_id)


def stop_game(bot, chat_id):
    """
    Deletes all data linked with this game and sends game result to user

    :type chat_id: int
    :type bot: Bot
    """
    chat = chats[chat_id]
    bot.sendMessage(chat_id, "Твой счет: {0}/{1}".format(str(chat["points"]),
                                                         str(len(chat["words"]))))
    del chats[chat_id]


def send_question(bot, chat_id):
    """
    Sends new question to user

    :type chat_id: int
    :type bot: Bot
    """
    chat = chats[chat_id]
    words = chat["words"]
    word = words[chat["index"]]
    chat["index"] += 1
    chat["word"] = word

    definition = definitions.pop(word)

    defs_to_send = [definition] + random.sample(list(definitions.values()), 2)

    definitions[word] = definition

    random.shuffle(defs_to_send)
    chat["question"] = defs_to_send

    bot.sendMessage(chat_id, "Какое из определений верно?\n{0}".format(word), reply_markup=reply_markup)
    for index, definition in enumerate(defs_to_send):
        bot.sendMessage(chat_id, "{0}: {1}".format(str(index + 1), definition))


def try_parse_int(string):
    try:
        return int(string)
    except ValueError:
        return None


def is_valid_answer(answer):
    return answer is not None and 1 <= answer <= 3


def handle_message(bot, update):
    """
    Handles user's answer

    :type update: Update
    :type bot: Bot
    """
    chat_id = update.message.chat_id

    if chat_id not in chats:
        send_start_game(bot, chat_id)
    else:
        answer = try_parse_int(update.message.text)
        if not is_valid_answer(answer):
            bot.sendMessage(chat_id,
                            "Пожалуйста, введи номер от 1 до 3 (или воспользуйся клавиатурой)",
                            reply_markup=reply_markup)
            return

        chat = chats[chat_id]
        if is_correct_answer(chat, answer):
            bot.sendMessage(chat_id, "Верный ответ! Ты заработал {0} балл(а/ов)".format(points_per_answer))
            chat["points"] += 1
        else:
            bot.sendMessage(chat_id, "К сожалению, ответ неверный")

        if len(chat["words"]) <= chat["index"]:
            bot.sendMessage(chat_id, "Игра окончена!")
            stop_game(bot, chat_id)
        else:
            bot.sendMessage(chat_id, "Следующий вопрос")
            send_question(bot, chat_id)


def is_correct_answer(chat, answer):
    question_answers = chat["question"]
    return question_answers[answer - 1] == definitions[chat["word"]]


def send_start_game(bot, chat_id):
    bot.sendMessage(chat_id, "Я хочу играть! Набери /start")


dispatcher.addTelegramCommandHandler("start", start)
dispatcher.addTelegramCommandHandler("stop", stop)
dispatcher.addTelegramMessageHandler(handle_message)

if __name__ == "__main__":
    updater.start_polling()
