from flask import Flask, request, redirect, url_for, render_template
from dotenv import load_dotenv
import telebot
import os
from app_folder.models.user import UserModel
from app_folder.keyboards import *

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__, template_folder='templates')

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    if UserModel.is_user(chat_id):
        usr = UserModel.get_user(chat_id)
        print(usr)
        if usr.get("user_name", None) is None:
            msg = bot.send_message(chat_id, "Hi! What is your name?")
            bot.register_next_step_handler(msg, process_name_step)
            return
        if usr.get("age", None) is None:
            msg = bot.send_message(chat_id, 'How old are you?')
            bot.register_next_step_handler(msg, process_age_step)
            return
        if usr.get("gander", None) is None:
            msg = bot.send_message(chat_id, 'What is your gender', reply_markup=gender_keyboard())
            bot.register_next_step_handler(msg, process_sex_step)
            return
        bot.send_message(chat_id, "You can change info in menu", reply_markup=main_menu_keyboard())
    else:
        msg = bot.send_message(chat_id, "Hi! What is your name?")
        bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    msg = bot.send_message(chat_id, 'How old are you?')
    UserModel.insert_one(tg_id=chat_id, user_name=name)
    bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    chat_id = message.chat.id
    age = message.text
    if not age.isdigit():
        msg = bot.send_message(chat_id, 'Age must be a number. How old are you?')
        bot.register_next_step_handler(msg, process_age_step)
        return
    UserModel.update(tg_id=chat_id, age=age)
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Male', 'Female')
    msg = bot.send_message(chat_id, 'What is your gender', reply_markup=markup)
    bot.register_next_step_handler(msg, process_sex_step)


def process_sex_step(message):
    chat_id = message.chat.id
    gender = message.text
    if gender != u'Male' and gender != u'Female':
        msg = bot.send_message(chat_id, 'Male or Female? What is your gender', reply_markup=gender_keyboard())
        bot.register_next_step_handler(msg, process_sex_step)
        return

    UserModel.update(tg_id=chat_id, gender=gender)
    get_info(message)


@bot.message_handler(regexp="Get my info")
def get_info(message):
    chat_id = message.chat.id
    usr = UserModel.get_user(tg_id=chat_id)
    name = usr["user_name"]
    age = usr["age"]
    gender = usr["gender"]
    bot.send_message(chat_id, f"Info:\nName: {name}\nAge: {age}\nGender: {gender}",
                     reply_markup=main_menu_keyboard())


@bot.message_handler(regexp="Change name")
def get_new_name(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Okay. Enter new name!', reply_markup=back_keyboard())
    bot.register_next_step_handler(msg, process_get_new_name)


def process_get_new_name(message):
    chat_id = message.chat.id
    if message.text != "Back to main menu":
        name = message.text
        UserModel.update(tg_id=chat_id, user_name=name)
        bot.send_message(chat_id, f'Great! New name: {name}', reply_markup=main_menu_keyboard())
    else:
        get_info(message)


@bot.message_handler(regexp="Change gender")
def get_new_gender(message):
    chat_id = message.chat.id
    if message.text != "Back to main menu":
        gender = message.text
        if gender != u'Male' and gender != u'Female':
            msg = bot.send_message(chat_id, 'Male or Female? What is your gender',
                                   reply_markup=new_gender_back_keyboard())

            bot.register_next_step_handler(msg, process_get_new_gender)
            return

        UserModel.update(tg_id=chat_id, gender=gender)
        bot.send_message(chat_id, f'Great! New gender: {gender}', reply_markup=main_menu_keyboard())
    else:
        get_info(message)


def process_get_new_gender(message):
    chat_id = message.chat.id
    if message.text != "Back to main menu":
        gender = message.text
        if gender != u'Male' and gender != u'Female':
            msg = bot.send_message(chat_id, 'Male or Female? What is your gender', reply_markup=gender_keyboard())
            bot.register_next_step_handler(msg, process_get_new_gender)
            return

        usr = UserModel.update(tg_id=chat_id, gender=gender)
        bot.send_message(chat_id, f'Great! New gender: {gender}', reply_markup=main_menu_keyboard())
    else:
        get_info(message)


@bot.message_handler(regexp="Change age")
def get_new_age(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Okay. Enter new age!', reply_markup=back_keyboard())
    bot.register_next_step_handler(msg, process_get_new_age)


def process_get_new_age(message):
    chat_id = message.chat.id
    if message.text != "Back to main menu":
        age = message.text
        if not age.isdigit():
            msg = bot.send_message(chat_id, 'Age must be a number. How old are you?',
                                   reply_markup=back_keyboard())
            bot.register_next_step_handler(msg, process_get_new_age)
            return
        usr = UserModel.get_user(chat_id)
        if age == usr["age"]:
            msg = bot.send_message(chat_id, f'{age} you have already entered. Enter new age',
                                   reply_markup=back_keyboard())
            bot.register_next_step_handler(msg, process_get_new_age)
            return
        UserModel.update(tg_id=chat_id, age=age)
        bot.send_message(chat_id, f'Great! New age: {age}', reply_markup=main_menu_keyboard())
    else:
        get_info(message)


@server.route("/send/", methods=['GET', 'POST'])
def send_admin():
    if request.method == 'POST':
        data = request.form
        text = data["text"]
        usrs = UserModel.get_all()
        err = []
        for usr in usrs:
            try:
                bot.send_message(usr["tg_id"], text)
            except telebot.apihelper.ApiException as e:
                chat_id = usr["tg_id"]
                err.append(f" ID: {chat_id} -- " + str(e))
        return "SENT" + '\n'.join(err)
    elif request.method == 'GET':
        return render_template('index.html')


@server.route('/bot/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    new_webhook_url = os.getenv("WEBHOOK_URL")
    bot.set_webhook(url=new_webhook_url + 'bot/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8000)))
