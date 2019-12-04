import telebot


def remove_keyboard():
    return telebot.types.ReplyKeyboardRemove()


def gender_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Male', 'Female')
    return markup


def main_menu_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Change name', 'Change gender', 'Change age')
    markup.add('Get my info')
    return markup


def back_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Back to main menu')
    return markup

def new_gender_back_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Male', 'Female')
    markup.add('Back to main menu')
    return markup

