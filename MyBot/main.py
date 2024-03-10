import telebot
from telebot import types
import requests
from datetime import datetime, timedelta
import pandas as pd
import yadisk

y = yadisk.YaDisk(token="y0_AgAAAABNWZOrAAtrUQAAAAD9wo8DAACEP7UX46JHGKIS8dDwccA7sDbE7A")

bot = telebot.TeleBot('7135590487:AAHv-sZ91-p1y9p9jsCn6vESSJ2wQfTP9Sg')
accounts = {}

# Ключ API Timeweb
TIMEWEB_API_KEY = 'your_timeweb_api_key'

# Функция для отправки запроса к API Timeweb
def check_hosting_payment(account_number):
    url = f'https://api.timeweb.com/v1/payments/{account_number}?apikey={TIMEWEB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('payment_date'), data.get('payment_amount')
    else:
        return None, None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('Получить список номеров телефонов из табличного документа')
    item2 = types.KeyboardButton('Работа с номерами телефонов и id пользователей')
    item3 = types.KeyboardButton('Работа с контактами в телеграм-канале')
    item4 = types.KeyboardButton('Работа с уведомлениями о сроках оплаты хостинга')
    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id, 'Привет {0.first_name}, Я бот для отслеживания сроков оплаты хостинга.'.format(message.from_user), reply_markup = markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text =='Получить список номеров телефонов из табличного документа':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Открыть файл с номерами телефонов локально')
            item2 = types.KeyboardButton('Открыть файл с номерами телефонов с Яндекс Диска')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Получить список номеров телефонов из табличного документа', reply_markup=markup)

        elif message.text =='Работа с номерами телефонов и id пользователей':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Показать список пользователей полностью')
            item2 = types.KeyboardButton('Поиск пользователя по номеру телефона')
            item3 = types.KeyboardButton('Добавить номер телефона')
            item4 = types.KeyboardButton('Удалить номер телефона')
            item5 = types.KeyboardButton('Редактировать номер телефона')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, item3, item4, item5, back)
            bot.send_message(message.chat.id, 'Работа с номерами телефонов и id пользователей', reply_markup=markup)

        elif message.text =='Работа с контактами в телеграм-канале':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Добавить пользователя')
            item2 = types.KeyboardButton('Удалить пользователя')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Работа с контактами в телеграм-канале', reply_markup=markup)

        elif message.text =='Работа с уведомлениями о сроках оплаты хостинга':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Добавить пользователя для мониторинга')
            item2 = types.KeyboardButton('Убрать пользователя c мониторинга')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Работа с уведомлениями о сроках оплаты хостинга', reply_markup=markup)

    #--------------------------Модули "Получить список номеров телефонов из табличного документа"------------------------

        elif message.text == 'Открыть файл с номерами телефонов локально':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Главное меню')
            markup.add(back)
            try:
                # Чтение файла Excel
                file = pd.read_excel('Static/Numbers.xlsx')

                # Извлечение номеров телефонов из первого столбца
                phone_numbers = file.iloc[:, 0].astype(str).tolist()
                accounts_data = file.iloc[:, 1].tolist()

                # Добавление номеров телефонов в массив accounts
                for phone_number, account_data in zip(phone_numbers, accounts_data):
                    accounts[phone_number] = account_data
                bot.send_message(message.chat.id, 'Список номеров телефонов из локального файла:')

                # Вывод списка номеров телефонов и связанных аккаунтов
                for phone_number, account_data in zip(phone_numbers, accounts_data):
                    bot.send_message(message.chat.id, f'Номер телефона: {phone_number}, Аккаунт: {account_data}')

            except Exception as e:
                bot.send_message(message.chat.id, f'Ошибка при открытии локального файла: {e}', reply_markup=markup)


        elif message.text == 'Открыть файл с номерами телефонов с Яндекс Диска':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Главное меню')
            markup.add(back)
            y.download("/numbers.xlsx", "yandex.xlsx")
            bot.send_message(message.chat.id, 'Меню работы с ссылкой чтения файла', reply_markup=markup)

            try:
                # Чтение файла Excel
                file = pd.read_excel('./yandex.xlsx')

                # Извлечение номеров телефонов из первого столбца
                phone_numbers = file.iloc[:, 0].astype(str).tolist()
                accounts_data = file.iloc[:, 1].astype(str).tolist()  # Извлечение аккаунтов из второго столбца

                # Добавление номеров телефонов и связанных аккаунтов в массив accounts
                for phone_number, account_data in zip(phone_numbers, accounts_data):
                    accounts[phone_number] = account_data
                bot.send_message(message.chat.id, 'Список номеров полученный с Яндес Диска:')

                # Вывод списка номеров телефонов и связанных аккаунтов
                for phone_number, account_data in zip(phone_numbers, accounts_data):
                    bot.send_message(message.chat.id, f'Номер телефона: {phone_number}, Аккаунт: {account_data}')


            except Exception as e:
                bot.send_message(message.chat.id, f'Ошибка при открытии файла с Яндекс Диска: {e}', reply_markup=markup)

        # --------------------------Модули "Работа с номерами телефонов и id пользователей"------------------------

        elif message.text == 'Показать список пользователей полностью':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Список всех номеров пользователей:', reply_markup=markup)

            # Проверяем, есть ли номера телефонов в списке
            if accounts:
                # Отправляем каждый номер телефона и связанный с ним аккаунт как отдельное сообщение
                for phone_number, account_data in accounts.items():
                    bot.send_message(message.chat.id, f'Номер телефона: {phone_number}, Аккаунт: {account_data}')
            else:
                bot.send_message(message.chat.id, 'Список номеров телефонов пуст.')


        elif message.text =='Поиск пользователя по номеру телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню поиска по номеру телефона', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона для поиска')
            bot.register_next_step_handler(message, search_account)

        elif message.text =='Добавить номер телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона, который хотите добавить')
            bot.register_next_step_handler(message, get_phone_number)

        elif message.text =='Удалить номер телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона, который хотите удалить')
            bot.register_next_step_handler(message, del_account)

        elif message.text =='Редактировать номер телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню редактирования номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона, который хотите отредактировать')
            bot.register_next_step_handler(message, edit_account)

        # --------------------------Модули "Работа с контактами в телеграм-канале"------------------------

        elif message.text =='Добавить пользователя':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с контактами в телеграм-канале')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления в Telegramm-канал', reply_markup=markup)
            bot.send_message(message.chat.id, 'Укажите ID пользователя, которого хотите добавить')
            bot.register_next_step_handler(message, add_telegramm)

        elif message.text =='Удалить пользователя':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с контактами в телеграм-канале')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню удаления из Telegramm-канала', reply_markup=markup)
            bot.send_message(message.chat.id, 'Укажите ID пользователя, которого хотите удалить из Telegramm-канала')
            bot.register_next_step_handler(message, del_telegramm)

        # --------------------------Модули "Работа с уведомлениями о сроках оплаты хостинга"------------------------

        elif message.text =='Добавить пользователя для мониторинга':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работа с уведомлениями')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления мониторинга пользователя', reply_markup=markup)
            bot.send_message(message.chat.id, 'Укажите ID пользователя, которого хотите мониторить')
            bot.register_next_step_handler(message, add_monitoring)

        elif message.text =='Убрать пользователя c мониторинга':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работа с уведомлениями')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню удаления мониторинга пользователя', reply_markup=markup)
            bot.send_message(message.chat.id, 'Укажите ID пользователя, у которого отмените мониторинг')
            bot.register_next_step_handler(message, del_monitoring)

        # --------------------------Модули "Назад"------------------------

        elif message.text == 'Главное меню':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Получить список номеров телефонов из табличного документа')
            item2 = types.KeyboardButton('Работа с номерами телефонов и id пользователей')
            item3 = types.KeyboardButton('Работа с контактами в телеграм-канале')
            item4 = types.KeyboardButton('Работа с уведомлениями о сроках оплаты хостинга')
            markup.add(item1, item2, item3, item4)

            bot.send_message(message.chat.id, 'Главное меню'.format(message.from_user), reply_markup=markup)

        elif message.text == 'Назад к работе с номерами телефонов':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Показать список пользователей полностью')
            item2 = types.KeyboardButton('Поиск пользователя по номеру телефона')
            item3 = types.KeyboardButton('Добавить номер телефона')
            item4 = types.KeyboardButton('Удалить номер телефона')
            item5 = types.KeyboardButton('Редактировать номер телефона')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, item3, item4, item5, back)
            bot.send_message(message.chat.id, 'Меню работы с номерами телефонов', reply_markup=markup)

        elif message.text == 'Назад к работе с контактами в телеграм-канале':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Добавить пользователя')
            item2 = types.KeyboardButton('Удалить пользователя')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Меню работы с контактами в телеграм-канале', reply_markup=markup)

        elif message.text == 'Назад к работа с уведомлениями':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Добавить пользователя для мониторинга')
            item2 = types.KeyboardButton('Убрать пользователя c мониторинга')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Меню работы с уведомлениями о сроках оплаты хостинга', reply_markup=markup)



def search_account(message):
    try:
        phone_number = message.text
        if phone_number in accounts:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} найден. Аккаунт: {accounts[phone_number]}')
        else:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} не найден.')
        bot.register_next_step_handler(message, start)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при поиске пользователя.')


def get_phone_number(message):
    try:
        phone_number = message.text
        bot.send_message(message.chat.id, 'Введите аккаунт:')
        bot.register_next_step_handler(message, add_account, phone_number)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении номера телефона.')


def add_account(message, phone_number):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        account = message.text
        accounts[phone_number] = account
        bot.send_message(message.chat.id,f'Номер телефона {phone_number} и связанный с ним аккаунт {account} успешно добавлены.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при добавлении номера телефона и аккаунта.')

def del_account(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        phone_number = message.text
        if phone_number in accounts:
            del accounts[phone_number]
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} успешно удален.')
        else:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при удалении пользователя.')

def edit_account(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        old_phone_number = message.text
        if old_phone_number in accounts:
            bot.send_message(message.chat.id, f'Введите новый номер телефона для замены {old_phone_number}:')
            bot.register_next_step_handler(message, lambda msg: get_new_phone(msg, old_phone_number))
        else:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {old_phone_number} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при редактировании номера телефона.', reply_markup=markup)

def get_new_phone(message, old_phone_number):
    try:
        new_phone_number = message.text
        bot.send_message(message.chat.id, f'Введите новый аккаунт для номера телефона {old_phone_number}:')
        bot.register_next_step_handler(message, lambda msg: get_new_account(msg, old_phone_number, new_phone_number))
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении нового номера телефона.')

def get_new_account(message, old_phone_number, new_phone_number):
    try:
        new_account = message.text
        update_account(message, old_phone_number, new_phone_number, new_account)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении нового аккаунта.')


def update_account(message, old_phone_number, new_phone_number, new_account):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        if old_phone_number in accounts:
            accounts[new_phone_number] = new_account  # Обновляем номер телефона и связанный аккаунт
            del accounts[old_phone_number]  # Удаляем старую запись
            bot.send_message(message.chat.id, f'Номер телефона {old_phone_number} успешно заменен на {new_phone_number} с аккаунтом {new_account}.')
        else:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {old_phone_number} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при обновлении номера телефона.', reply_markup=markup)
def add_telegramm(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        user_id = int(message.text)
        # Нужно получить id пользователей
        # Логика добавления пользователя в телеграм-канал
        # Пример:
        # bot.add_to_chat(user_id, 'название_телеграм_канала')
        bot.send_message(message.chat.id, f'Пользователь с ID {user_id} успешно добавлен в телеграм-канал.')
    except ValueError:
        bot.send_message(message.chat.id, 'ID пользователя должен быть числом. Попробуйте снова.')
        bot.register_next_step_handler(message, add_telegramm)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при добавлении пользователя в телеграм-канал.', reply_markup=markup)

def del_telegramm(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        user_id = int(message.text)
        # Логика удаления пользователя из телеграм-канала
        # Например, используя библиотеку Telethon или pyTelegramBotAPI
        # Пример:
        # bot.remove_from_chat(user_id, 'название_телеграм_канала')
        bot.send_message(message.chat.id, f'Пользователь с ID {user_id} успешно удален из телеграм-канала.')
    except ValueError:
        bot.send_message(message.chat.id, 'ID пользователя должен быть числом. Попробуйте снова.')
        bot.register_next_step_handler(message, del_telegramm)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при удалении пользователя из телеграм-канала.', reply_markup=markup)

def add_monitoring(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        user_id = int(message.text)
        # Логика добавления пользователя для мониторинга оплаты хостинга
        # Например, добавление пользователя в список для дальнейшего мониторинга
        bot.send_message(message.chat.id, f'Пользователь с ID {user_id} добавлен для мониторинга оплаты хостинга.')
    except ValueError:
        bot.send_message(message.chat.id, 'ID пользователя должен быть числом. Попробуйте снова.')
        bot.register_next_step_handler(message, add_monitoring)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при добавлении пользователя для мониторинга оплаты хостинга.', reply_markup=markup)

def del_monitoring(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        user_id = int(message.text)
        # Логика удаления пользователя из мониторинга оплаты хостинга
        # Например, удаление пользователя из списка мониторинга
        bot.send_message(message.chat.id, f'Пользователь с ID {user_id} удален из мониторинга оплаты хостинга.')
    except ValueError:
        bot.send_message(message.chat.id, 'ID пользователя должен быть числом. Попробуйте снова.')
        bot.register_next_step_handler(message, del_monitoring)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при удалении пользователя из мониторинга оплаты хостинга.', reply_markup=markup)





# Функция для проверки сроков оплаты и отправки уведомлений
def check_payment_due(message):
    for account_number in accounts:
        payment_date, payment_amount = check_hosting_payment(account_number)
        if payment_date:
            due_date = datetime.strptime(payment_date, '%Y-%m-%d') - timedelta(days=30)
            if datetime.now() >= due_date:
                bot.send_message(message.chat.id, f'Оплата хостинга {account_number} на сумму {payment_amount}. Хостинг отключится {payment_date}')

bot.polling(none_stop=True)