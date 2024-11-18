from http.client import responses
import telebot
import requests
import json

from telebot.apihelper import send_message
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from requ import *

token="7162249200:AAEDzqbzwiHbOufNtFkERk4ot304dX1F_cM"
bot=telebot.TeleBot(token)

class Authorization():
    def __init__(self, tenant_ID, number):
        self.number = number
        self.tenant_ID = tenant_ID
    def data(self, current_apartment):
        self.current_apartment = current_apartment
users = {0 : 0}
ids = {}
@bot.message_handler(commands=['buffer'])
def buffer(message):
    bot.send_message(message.chat.id, message.chat.id)

@bot.message_handler(commands=['users'])
def users_show(message):
    bot.send_message(message.chat.id, users[message.chat.id].tenant_ID)


@bot.message_handler(commands=['authorize', 'start'])
def tenant_id(message):
    global user_number, tenant_flag
    tenant_flag = 0
    print("Создан запрос на авторизацию")
    bot.send_message(message.chat.id, "Здравствуйте, я чат бот для управления вашими домофонами!")
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton("Отправить номер телефона 📞", request_contact=True)
    markup.add(button)
    bot.send_message(message.chat.id,"Пожалуйста, отправьте свой номер телефона для авторизации, нажав на кнопку ниже:", reply_markup=markup)
@bot.message_handler(content_types=['contact'])
def number_save(message):
    global user_number, tenant_flag
    user_number = message.contact.phone_number.replace(" ", "")[1:]

    responce = check_tenant(user_number)

    match responce.status_code == 200:
        case (True):
            users[message.chat.id] = Authorization(responce.text[13:-1], user_number)
            ids[user_number] = message.chat.id
            print("Успешная авторизация", message.chat.id, users)
            bot.send_message(message.chat.id, "Вы успешно авторизовались!", reply_markup=telebot.types.ReplyKeyboardRemove())
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button = telebot.types.KeyboardButton("Мои квартиры")
            markup.add(button)
            bot.send_message(message.chat.id, "Удачного пользования нашим сервисом!", reply_markup=markup)
        case (False):
            bot.send_message(message.chat.id, "Номер телефона не найден", reply_markup=telebot.types.ReplyKeyboardRemove())


all_apartments = []
all_domo = []
domo_id = 0
@bot.message_handler(func=lambda message: message.text == "Мои квартиры")
def my_apartments(message):
    print("Мои квартиры")
    global all_apartments, apartments
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    apartments = domo_apartment(users[message.chat.id].tenant_ID)
    for i in apartments:
        markup.add(f"{i[2]}, {i[1]}")
        all_apartments += [f"{i[2]}, {i[1]}"]
    bot.send_message(message.chat.id, "Нажмите на квартиру, чтобы показать доступные домофоны", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Вернуться в квартиры")
def return_to_aps(message):
    global all_apartments, apartments
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    apartments = domo_apartment(users[message.chat.id].tenant_ID)
    for i in apartments:
        markup.add(f"{i[2]}, {i[1]}")
        all_apartments += [f"{i[2]}, {i[1]}"]
    bot.send_message(message.chat.id, "Нажмите на квартиру, чтобы показать доступные домофоны", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in all_apartments)
def get_domophones(message, prev_apartment=""):
    global all_domo
    if prev_apartment == "":
        users[message.chat.id].current_apartment = message.text
    apartment = users[message.chat.id].current_apartment[users[message.chat.id].current_apartment.find(", ")+2:]
    for i in apartments:
        if apartment == i[1]:
            apartment = i[0]

    domophons = get_domophons(users[message.chat.id].tenant_ID, apartment)
    markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in domophons:
        markup.add(telebot.types.KeyboardButton(f"{i[1]} №{i[0]}"))
        all_domo += [f"{i[1]} №{i[0]}"]
    markup.add("Вернуться в квартиры")
    print(all_domo)
    bot.send_message(message.chat.id, "Список доступных домофонов:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in all_domo)
def domo_menu(message):
    global domo_id
    domo_id = message.text[message.text.find("№")+1:]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    domo_open = telebot.types.KeyboardButton("Открыть домофон")
    domo_photo = telebot.types.KeyboardButton("Посмотреть снимок с камеры")
    domo_back = telebot.types.KeyboardButton("Вернуться к домофонам")
    markup.add(domo_open, domo_photo)
    markup.add(domo_back)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Вернуться к домофонам")
def back(message, prev_apartment=""):
    global all_domo
    apartment = users[message.chat.id].current_apartment[users[message.chat.id].current_apartment.find(", ")+2:]
    for i in apartments:
        if apartment == i[1]:
            apartment = i[0]

    domophons = get_domophons(users[message.chat.id].tenant_ID, apartment)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in domophons:
        markup.add(telebot.types.KeyboardButton(f"{i[1]} №{i[0]}"))
        all_domo += [f"{i[1]} №{i[0]}"]
    bot.send_message(message.chat.id, "Список доступных домофонов:", reply_markup=markup)


photo_flag = 1
@bot.message_handler(func=lambda message: message.text == "Посмотреть снимок с камеры")
def get_domophone_photo(message):
    global domo_id
    photo = get_photo(domo_id, users[message.chat.id].tenant_ID)
    if photo[1] == 200  :
        bot.send_photo(message.chat.id, photo[0])
    else:
        bot.send_photo(message.chat.id, f"Ошибка {photo[1]}")


@bot.message_handler(func=lambda message: message.text == "Открыть домофон")
def open(message):
    global domo_id
    response = open_domophon(users[message.chat.id].tenant_ID, domo_id)
    if response == 200:
        bot.send_message(message.chat.id, "Домофон открыт")
    else:
        bot.send_message(message.chat.id, f"Ошибка {response}")




@bot.message_handler(func=lambda message: message.text not in all_domo and message.text not in all_apartments)
def unsupported(message):
    bot.send_message(message.chat.id, "Не-а")







bot.infinity_polling()

