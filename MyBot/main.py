import telebot
from telebot import types
import requests
from datetime import datetime, timedelta
import pandas as pd
import yadisk

y = yadisk.YaDisk(token="Ваш_токен_яндекса")

bot = telebot.TeleBot('ID_Вашего_бота')
accounts = {}
monitored_users = {}

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

def convert_to_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('Получить список номеров телефонов из табличного документа')
    item2 = types.KeyboardButton('Работа с аккаунтами')
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

        elif message.text =='Работа с аккаунтами':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Показать список пользователей полностью')
            item2 = types.KeyboardButton('Поиск пользователя по номеру телефона')
            item3 = types.KeyboardButton('Добавить пользователя TimeWeb')
            item4 = types.KeyboardButton('Удалить пользователя TimeWeb')
            item5 = types.KeyboardButton('Меню редактирования')
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
            item3 = types.KeyboardButton('Показать список мониторинга')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, item3, back)
            bot.send_message(message.chat.id, 'Работа с уведомлениями о сроках оплаты хостинга', reply_markup=markup)

        elif message.text =='Меню редактирования':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item5 = types.KeyboardButton('Редактировать номер телефона')
            item6 = types.KeyboardButton('Редактировать аккаунт')
            item7 = types.KeyboardButton('Редактировать цену тарифа')
            item8 = types.KeyboardButton('Редактировать последнюю дату оплаты')
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(item5, item6, item7, item8, back)
            bot.send_message(message.chat.id, 'Работа с номерами телефонов и id пользователей', reply_markup=markup)

    #--------------------------Модули "Получить список номеров телефонов из табличного документа"------------------------

        elif message.text == 'Открыть файл с номерами телефонов локально':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Главное меню')
            markup.add(back)
            try:
                # Чтение файла Excel
                file = pd.read_excel('Static/Numbers.xlsx')

                # Извлечение данных из соответствующих столбцов
                phone_numbers = file.iloc[:, 0].astype(str).tolist()
                accounts_data = file.iloc[:, 1].astype(str).tolist()
                tariffs = [convert_to_float(tariff) for tariff in file.iloc[:, 2].tolist()]
                last_payment_dates = [convert_to_date(date_str) for date_str in file.iloc[:, 3].astype(str).tolist()]

                # Добавление информации в словарь accounts
                for phone_number, account_data, tariff, last_payment_date in zip(phone_numbers, accounts_data, tariffs,
                                                                                 last_payment_dates):
                    accounts[phone_number] = {'account': account_data,
                                              'tariff': tariff,
                                              'last_payment_date': last_payment_date}

                bot.send_message(message.chat.id, 'Список номеров телефонов из локального файла:')

                # Вывод списка номеров телефонов и связанных данных
                for phone_number, data in accounts.items():
                    bot.send_message(message.chat.id,
                                     f'Номер телефона: {phone_number}, Аккаунт: {data["account"]}, Тариф: {data["tariff"]}, Последняя дата оплаты: {data["last_payment_date"]}')

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
                # Извлечение данных из соответствующих столбцов
                phone_numbers = file.iloc[:, 0].astype(str).tolist()
                accounts_data = file.iloc[:, 1].astype(str).tolist()
                tariffs = [convert_to_float(tariff) for tariff in file.iloc[:, 2].astype(str).tolist()]
                last_payment_dates = [convert_to_date(date_str) for date_str in file.iloc[:, 3].astype(str).tolist()]

                # Добавление информации в словарь accounts
                for phone_number, account_data, tariff, last_payment_date in zip(phone_numbers, accounts_data, tariffs, last_payment_dates):
                    accounts[phone_number] = {'account': account_data,
                                              'tariff': tariff,
                                              'last_payment_date': last_payment_date}
                bot.send_message(message.chat.id, 'Список номеров полученный с Яндес Диска:')

                # Вывод списка номеров телефонов и связанных данных
                for phone_number, data in accounts.items():
                    bot.send_message(message.chat.id,
                                     f'Номер телефона: {phone_number}, Аккаунт: {data["account"]}, Тариф: {data["tariff"]}, Последняя дата оплаты: {data["last_payment_date"]}')

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
                # Отправляем каждую запись в списке как отдельное сообщение
                for phone_number, user_info in accounts.items():
                    account_info = f'Аккаунт: {user_info["account"]}, Тариф: {user_info["tariff"]}, Последняя дата оплаты: {user_info["last_payment_date"]}'
                    bot.send_message(message.chat.id, f'Номер телефона: {phone_number}, {account_info}')
            else:
                bot.send_message(message.chat.id, 'Список номеров телефонов пуст.')


        elif message.text =='Поиск пользователя по номеру телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню поиска по номеру телефона', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона для поиска')
            bot.register_next_step_handler(message, search_account)

        elif message.text =='Добавить пользователя TimeWeb':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона, который хотите добавить')
            bot.register_next_step_handler(message, get_phone_number)

        elif message.text =='Удалить пользователя TimeWeb':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню добавления номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона пользователя, о котором хотите стереть информацию')
            bot.register_next_step_handler(message, del_account)

        elif message.text =='Редактировать номер телефона':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню редактирования номеров', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите номер телефона, который хотите отредактировать')
            bot.register_next_step_handler(message, edit_nomer)

        elif message.text =='Редактировать аккаунт':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню редактирования аккаунтов', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите аккаунт, который хотите отредактировать')
            bot.register_next_step_handler(message, edit_account)

        elif message.text =='Редактировать цену тарифа':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню редактирования цен', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите аккаунт у которого хотите изменить цену тарифа')
            bot.register_next_step_handler(message, edit_price)

        elif message.text =='Редактировать последнюю дату оплаты':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работе с номерами телефонов')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню редактирования дат', reply_markup=markup)
            bot.send_message(message.chat.id, 'Введите аккаунт у которго хотите изменить дату последней оплаты')
            bot.register_next_step_handler(message, edit_date)

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
            bot.send_message(message.chat.id, 'Укажите аккаунт пользователя, которого хотите мониторить')
            bot.register_next_step_handler(message, add_monitoring)

        elif message.text =='Убрать пользователя c мониторинга':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работа с уведомлениями')
            markup.add(back)
            bot.send_message(message.chat.id, 'Меню удаления мониторинга пользователя', reply_markup=markup)
            bot.send_message(message.chat.id, 'Укажите аккаунт пользователя, у которого отмените мониторинг')
            bot.register_next_step_handler(message, del_monitoring)


        elif message.text == 'Показать список мониторинга':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад к работа с уведомлениями')
            markup.add(back)
            bot.send_message(message.chat.id, 'Список всех отслеживаемых аккаунтов:', reply_markup=markup)
            try:
                # Проверяем, есть ли пользователи для мониторинга в списке
                if monitored_users:
                    # Отправляем каждого пользователя в списке как отдельное сообщение
                    for account, user_info in monitored_users.items():
                        account_info = f'Аккаунт: {account}, Тариф: {user_info["tariff"]}, Последняя дата оплаты: {user_info["last_payment_date"]}'
                        bot.send_message(message.chat.id, account_info, reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, 'Список пользователей для мониторинга пуст.', reply_markup=markup)
            except Exception as e:
                bot.send_message(message.chat.id, f'Ошибка при отображении списка пользователей для мониторинга: {e}',
                                 reply_markup=markup)

        # --------------------------Модули "Назад"------------------------

        elif message.text == 'Главное меню':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Получить список номеров телефонов из табличного документа')
            item2 = types.KeyboardButton('Работа с аккаунтами')
            item3 = types.KeyboardButton('Работа с контактами в телеграм-канале')
            item4 = types.KeyboardButton('Работа с уведомлениями о сроках оплаты хостинга')
            markup.add(item1, item2, item3, item4)

            bot.send_message(message.chat.id, 'Главное меню'.format(message.from_user), reply_markup=markup)

        elif message.text == 'Назад к работе с номерами телефонов':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Показать список пользователей полностью')
            item2 = types.KeyboardButton('Поиск пользователя по номеру телефона')
            item3 = types.KeyboardButton('Добавить пользователя TimeWeb')
            item4 = types.KeyboardButton('Удалить пользователя TimeWeb')
            item5 = types.KeyboardButton('Меню редактирования')
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
            item3 = types.KeyboardButton('Показать список мониторинга')
            back = types.KeyboardButton('Главное меню')
            markup.add(item1, item2, item3, back)
            bot.send_message(message.chat.id, 'Меню работы с уведомлениями о сроках оплаты хостинга', reply_markup=markup)



def search_account(message):
    try:
        phone_number = message.text
        if phone_number in accounts:
            account_info = accounts[phone_number]
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} найден.')
            bot.send_message(message.chat.id, f'Информация о пользователе:')
            bot.send_message(message.chat.id, f'Номер телефона: {phone_number}')
            bot.send_message(message.chat.id, f'Аккаунт: {account_info["account"]}')
            bot.send_message(message.chat.id, f'Тариф: {account_info["tariff"]}')
            bot.send_message(message.chat.id, f'Последняя дата оплаты: {account_info["last_payment_date"]}')
        else:
            bot.send_message(message.chat.id, f'Пользователь с номером телефона {phone_number} не найден.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при поиске пользователя.')



def get_phone_number(message):
    try:
        phone_number = message.text
        bot.send_message(message.chat.id, 'Введите аккаунт:')
        bot.register_next_step_handler(message, get_account, phone_number)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении номера телефона.')

# Функция для запроса аккаунта
def get_account(message, phone_number):
    try:
        account = message.text
        bot.send_message(message.chat.id, 'Введите цену (число с плавающей точкой):')
        bot.register_next_step_handler(message, get_tariff, phone_number, account)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении аккаунта.')

# Функция для запроса тарифа
def get_tariff(message, phone_number, account):
    try:
        tariff = convert_to_float(message.text)
        if tariff is None:
            bot.send_message(message.chat.id, 'Цена должна быть числом с плавающей точкой. Пожалуйста, введите цену еще раз:')
            bot.register_next_step_handler(message, get_tariff, phone_number, account)
            return
        bot.send_message(message.chat.id, 'Введите последнюю дату оплаты (в формате ГГГГ-ММ-ДД):')
        bot.register_next_step_handler(message, add_data, phone_number, account, tariff)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении цены.')

# Функция для добавления данных о телефоне в словарь
def add_data(message, phone_number, account, tariff):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        last_payment_date = convert_to_date(message.text)
        if last_payment_date is None:
            bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, введите дату еще раз (в формате ГГГГ-ММ-ДД):')
            bot.register_next_step_handler(message, add_data, phone_number, account, tariff)
            return
        accounts[phone_number] = {'account': account, 'tariff': tariff, 'last_payment_date': last_payment_date}
        bot.send_message(message.chat.id, f'Номер телефона {phone_number}, аккаунт {account}, цена {tariff}, последняя дата оплаты {last_payment_date} успешно добавлены.', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при добавлении данных о номере телефона.')


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

def edit_nomer(message):
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
        if new_phone_number not in accounts:
            accounts[new_phone_number] = accounts.pop(old_phone_number)
            bot.send_message(message.chat.id, f'Номер телефона {old_phone_number} успешно заменен на {new_phone_number}.')
        else:
            bot.send_message(message.chat.id, f'Номер телефона {new_phone_number} уже существует.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении нового номера телефона.')


def edit_account(message):
    try:
        old_account = message.text
        account_info = None
        for phone_number, user_info in accounts.items():
            if user_info['account'] == old_account:
                account_info = user_info
                break

        if account_info is not None:
            bot.send_message(message.chat.id, f'Введите новый аккаунт для замены {old_account}:')
            bot.register_next_step_handler(message, lambda msg: get_new_account(msg, old_account))
        else:
            bot.send_message(message.chat.id, f'Аккаунт {old_account} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при редактировании аккаунта.')


def get_new_account(message, old_account):
    try:
        new_account = message.text
        for phone_number, user_info in accounts.items():
            if user_info['account'] == old_account:
                user_info['account'] = new_account
        bot.send_message(message.chat.id, f'Аккаунт {old_account} успешно заменен на {new_account}.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении нового аккаунта.')



def edit_price(message):
    try:
        account = message.text
        if account in [user_info['account'] for user_info in accounts.values()]:
            bot.send_message(message.chat.id, f'Введите новую цену тарифа для аккаунта {account}:')
            bot.register_next_step_handler(message, lambda msg: get_new_price(msg, account))
        else:
            bot.send_message(message.chat.id, f'Аккаунт {account} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при редактировании цены тарифа.')




def get_new_price(message, account):
    try:
        new_price = float(message.text)
        for phone_number, user_info in accounts.items():
            if user_info['account'] == account:
                user_info['tariff'] = new_price
        bot.send_message(message.chat.id, f'Цена тарифа для аккаунта {account} успешно изменена на {new_price}.')
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число для цены тарифа.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении новой цены тарифа.')




def edit_date(message):
    try:
        account = message.text
        if account in [user_info['account'] for user_info in accounts.values()]:
            bot.send_message(message.chat.id, f'Введите новую дату последней оплаты для аккаунта {account} в формате ГГГГ-ММ-ДД:')
            bot.register_next_step_handler(message, lambda msg: get_new_date(msg, account))
        else:
            bot.send_message(message.chat.id, f'Аккаунт {account} не найден в списке.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при редактировании даты последней оплаты.')

def get_new_date(message, account):
    try:
        new_date = datetime.strptime(message.text, '%Y-%m-%d').date()
        for phone_number, user_info in accounts.items():
            if user_info['account'] == account:
                user_info['last_payment_date'] = new_date
        bot.send_message(message.chat.id, f'Дата последней оплаты для аккаунта {account} успешно изменена на {new_date}.')
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении новой даты последней оплаты.')





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

# Функция добавления пользователя для мониторинга

def add_monitoring(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)

    account = message.text
    # Проверяем, существует ли указанный аккаунт в ключах словаря accounts
    if account in [user_info['account'] for user_info in accounts.values()]:
        # Получаем данные о тарифе и последней дате оплаты из словаря
        for phone_number, data in accounts.items():
            if data['account'] == account:
                tariff = data['tariff']
                last_payment_date = data['last_payment_date']
                # Добавляем пользователя для мониторинга в словарь, используя аккаунт в качестве ключа
                monitored_users[account] = {'tariff': tariff, 'last_payment_date': last_payment_date}
                bot.send_message(message.chat.id, f'Пользователь с аккаунтом {account} добавлен для мониторинга оплаты хостинга.', reply_markup=markup)
                break
    else:
        bot.send_message(message.chat.id, f'Аккаунт {account} не найден в списке.', reply_markup=markup)



# Функция удаления пользователя с мониторинга
def del_monitoring(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Главное меню')
    markup.add(back)
    try:
        # Получаем аккаунт пользователя для удаления мониторинга
        account = message.text
        # Проверяем, существует ли указанный аккаунт в списке мониторинга
        if account in monitored_users:
            # Удаляем пользователя из списка мониторинга
            del monitored_users[account]
            bot.send_message(message.chat.id, f'Мониторинг для пользователя с аккаунтом {account} успешно отменен.', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f'Пользователь с аккаунтом {account} не найден в списке мониторинга.', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при удалении пользователя с мониторинга: {e}', reply_markup=markup)






# Функция для проверки сроков оплаты и отправки уведомлений
def check_payment_due(message):
    for account_number in accounts:
        payment_date, payment_amount = check_hosting_payment(account_number)
        if payment_date:
            due_date = datetime.strptime(payment_date, '%Y-%m-%d') - timedelta(days=30)
            if datetime.now() >= due_date:
                bot.send_message(message.chat.id, f'Оплата хостинга {account_number} на сумму {payment_amount}. Хостинг отключится {payment_date}')

bot.polling(none_stop=True)
