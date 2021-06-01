import os
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

# If you getting an error in Chatterbot compat.py file in line 264
# Change the if statement there to "time_func = time.time"

# SETUP #########################################################

BOT_NAME = 'ChatCharlie'
ENDING_WORD = 'Tchau'
LANGUAGE = 'portuguese'
RESET_BOT = True

IMPORT_WHATSAPP_FILE = True
WHATSAPP_IMPORT_FILE_PATH = 'sample-whatsapp-chat.txt'
FIRST_WHATSAPP_USERNAME = 'Fulano'
SECOND_WHATSAPP_USERNAME = 'Ciclano'

# END #############################################################


def process_whatsapp_line(line):
    array = line.split(':')
    if len(array) > 2:
        array.pop(0)
        array.pop(0)
        text = " ".join(array) if len(array) > 1 else array[0]
        return text
    else:
        return ""


def import_whatsapp_txt(file, first_username, second_username):
    if os.stat(file).st_size == 0:
        return []
    try:
        text = open(file, "r", encoding="utf8").read()
    except():
        return []

    lines = text.split('\n')
    last_message = ''
    train_array = []

    for i, line in enumerate(lines):
        if first_username in line or second_username in line:
            current_user = first_username if first_username in line else second_username
            if i == len(lines) - 1:
                train_array.append(last_message if last_message != '' else process_whatsapp_line(line))
            elif current_user in lines[i + 1]:
                last_message = last_message + " " + process_whatsapp_line(line)
            else:
                train_array.append((last_message + " " + process_whatsapp_line(line)
                                    if last_message != '' else process_whatsapp_line(line)).strip())
                last_message = ''

    return train_array


def create_bot(name, language, wp_import, wp_import_path, wp_1st_username, wp_2nd_username, reset):
    bot = ChatBot(
        name,
        logic_adapters=[
            'chatterbot.logic.BestMatch', 'chatterbot.logic.MathematicalEvaluation', 'chatterbot.logic.BestMatch'],
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri='sqlite:///database.sqlite3',
    )

    if reset:
        bot.storage.drop()

    conversation = ChatterBotCorpusTrainer(bot)
    conversation.train('chatterbot.corpus.' + language)

    sample_array_train = [
        'Oi',
        'Olá como vai você?',
        'Qual o seu nome?',
        'Meu nome é ' + name + ' e o seu?',
        'Por que seu nome é ' + name + '?',
        'Foi inspirado no gato da pessoa que me criou',
        'Prazer em te conhecer',
        'O prazer é todo meu',
        'Quantos anos você tem?',
        'Sou novo tenho nasci em 2021',
        'Do que você gosta?',
        'Gosto de tecnologia',
        'Qual o seu filme favorito?',
        'Eu robô',
        'Qual a sua bebida favorita?',
        'Infelizmente não posso beber nada',
        'O que você faz?',
        'Eu respondo você',
        'Obrigado',
        'De nada'
    ]

    conversation = ListTrainer(bot)
    conversation.train(sample_array_train)

    if wp_import:
        array_train = import_whatsapp_txt(wp_import_path, wp_1st_username, wp_2nd_username)
        conversation.train(array_train)

    return bot


def run(name, ending_word, language, wp_import, wp_import_path, wp_1st_username, wp_2nd_username, reset):
    bot = create_bot(name, language, wp_import, wp_import_path, wp_1st_username, wp_2nd_username, reset)
    while True:
        user_input = input("User: ")
        if user_input.lower() != ending_word.lower():
            try:
                answer = bot.get_response(user_input)
                print(name + ": ", answer)
            except(KeyboardInterrupt, EOFError, SystemExit):
                break
        else:
            break


if __name__ == '__main__':
    run(BOT_NAME, ENDING_WORD, LANGUAGE, IMPORT_WHATSAPP_FILE, WHATSAPP_IMPORT_FILE_PATH,
        FIRST_WHATSAPP_USERNAME, SECOND_WHATSAPP_USERNAME, RESET_BOT)
