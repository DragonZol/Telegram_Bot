import telebot
from telebot import types
from datetime import datetime, timedelta
import pandas as pd
import yadisk
import schedule
import time
import threading

y = yadisk.YaDisk(token="y0_AgAAAABNWZOrAAtrUQAAAAD9wo8DAACEP7UX46JHGKIS8dDwccA7sDbE7A")

bot = telebot.TeleBot('7135590487:AAHv-sZ91-p1y9p9jsCn6vESSJ2wQfTP9Sg')
accounts = {}
monitored_users = {}

# Ключ API Timeweb
TIMEWEB_API_KEY = 'your_timeweb_api_key'


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
    # Создаем клавиатуру с основными функциями бота
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Добавь меня в список для мониторинга')
    item2 = types.KeyboardButton('Покажи сколько дней осталось до оплаты')
    markup.add(item1, item2)
    bot.send_message(message.chat.id,
                     'Привет {0.first_name}, Я бот для отслеживания сроков оплаты хостинга.'.format(message.from_user),
                     reply_markup=markup)
    check_payment_due()
    print(accounts)


@bot.message_handler(commands=['manager'])
def manager(message):
    # Проверяем, является ли отправитель сообщения менеджером (для примера - проверка по ID пользователя)
    if message.from_user.id == 1195491333:
        # Создаем клавиатуру с основными функциями бота
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Получить список номеров телефонов из табличного документа')
        item2 = types.KeyboardButton('Выведи список мониторинга')
        item3 = types.KeyboardButton('Выведи полный список пользователей со скорой оплатой')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id,
                         'Привет Менеджер, это клавиатура для удобного управления'.format(message.from_user),
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы не являетесь менеджером.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Обработка команды "Получить список номеров телефонов из табличного документа"
    if message.text == 'Получить список номеров телефонов из табличного документа':
        try:
            # Скачиваем файл с Яндекс Диска
            y.download("/numbers.xlsx", "yandex.xlsx")
            # Читаем файл Excel
            file = pd.read_excel('./yandex.xlsx')
            # Извлекаем данные из файла
            accounts.clear()
            for _, row in file.iterrows():
                phone_number = str(row['Номер телефона'])
                time_web_account = row['TimeWeb аккаунт']
                tariff = convert_to_float(row['Цена тарифа'])
                last_payment_date = row['Последний день оплаты'].strftime('%Y-%m-%d')
                last_payment_date = convert_to_date(last_payment_date)
                if phone_number in accounts:
                    accounts[phone_number].append({'time_web_account': time_web_account, 'tariff': tariff, 'last_payment_date': last_payment_date})
                else:
                    accounts[phone_number] = [{'time_web_account': time_web_account, 'tariff': tariff, 'last_payment_date': last_payment_date}]

            # Выводим список номеров телефонов и связанных данных
            response_message = 'Список номеров полученный с Яндекс Диска:\n'
            for phone_number, account_list in accounts.items():
                for account in account_list:
                    response_message += f'Номер телефона: {phone_number}, Аккаунт TimeWeb: {account["time_web_account"]}, Цена тарифа: {account["tariff"]}, Последний день оплаты: {account["last_payment_date"]}\n'
            bot.send_message(message.chat.id, response_message)

        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при открытии файла с Яндекс Диска: {e}')


    elif message.text == 'Добавь меня в список для мониторинга':
        bot.send_message(message.chat.id, "Введите ваш номер телефона:")
        bot.register_next_step_handler(message, process_phone_number)

    elif message.text == 'Выведи список мониторинга':
        display_monitored_list(message)

    elif message.text == 'Покажи сколько дней осталось до оплаты':
        show_days_until_payment(message)

    elif message.text == 'Выведи полный список пользователей со скорой оплатой':
        display_users_with_pending_payments(message)


# Функция для обработки номера телефона пользователя и его ID
def process_phone_number(message):
    # Получаем номер телефона от пользователя
    phone_number = message.text.strip()
    user_id = message.from_user.id
    monitored_users[phone_number] = user_id
    bot.send_message(message.chat.id, f"Вы успешно добавлены в список для мониторинга!")


# Функция для вывода списка пользователей под мониторингом
def display_monitored_list(message):
    response_message = "Список пользователей под мониторингом:\n"
    for phone_number, user_id in monitored_users.items():
        response_message += f'Номер телефона: {phone_number}, ID пользователя: {user_id}\n'
    bot.send_message(message.chat.id, response_message)


# Функция для проверки сроков оплаты и отправки уведомлений
def check_payment_due():
    for phone_number, account_list in accounts.items():
        for account in account_list:
            last_payment_date = account.get('last_payment_date')
            if last_payment_date:
                due_date = last_payment_date - timedelta(days=10)  # Проверяем, если оплата через 10 дней или меньше
                if datetime.now() >= datetime.combine(due_date, datetime.min.time()):
                    # Проверяем, есть ли пользователь с данным номером телефона в списке мониторинга
                    user_id = monitored_users.get(phone_number)
                    if user_id:
                        # Отправляем сообщение пользователю
                        time_web_account = account.get('time_web_account')
                        tariff = account.get('tariff')
                        bot.send_message(user_id,
                                         f'Оплата хостинга на аккаунте {time_web_account} суммой {tariff} должна быть проведена до {last_payment_date}')

# Функция для вывода информации о днях до оплаты
def show_days_until_payment(message):
    user_id = message.from_user.id
    if user_id in monitored_users.values():
        user_info = []
        for phone_number, account_list in accounts.items():
            for account in account_list:
                if monitored_users.get(phone_number) == user_id:
                    last_payment_date = account.get('last_payment_date')
                    if last_payment_date:
                        days_until_payment = (last_payment_date - datetime.now().date()).days
                        time_web_account = account.get('time_web_account')
                        tariff = account.get('tariff')
                        user_info.append(f'Хостинг {time_web_account}: Оплата до: {last_payment_date}, '
                                         f'Дней до оплаты: {days_until_payment}, Стоимость: {tariff}')
        if user_info:
            bot.send_message(user_id, '\n'.join(user_info))
        else:
            bot.send_message(user_id, 'У вас нет хостингов в списке мониторинга.')
    else:
        bot.send_message(user_id, 'Вы не добавлены в список мониторинга.')

# Функция для вывода списка пользователей со скорой оплатой
def display_users_with_pending_payments(message):
    # Проверяем, является ли отправитель сообщения менеджером (для примера - проверка по ID пользователя)
    if message.from_user.id == 1195491333:
        users_to_notify = []
        # Проверяем каждого пользователя в аккаунтах
        for phone_number, account_list in accounts.items():
            for account in account_list:
                last_payment_date = account.get('last_payment_date')
                if last_payment_date:
                    due_date = last_payment_date - timedelta(days=10)
                    if datetime.now() >= datetime.combine(due_date, datetime.min.time()):
                        # Если осталось меньше 10 дней на оплату, добавляем пользователя в список для уведомления
                        users_to_notify.append((phone_number, account['time_web_account'], last_payment_date))

        if users_to_notify:
            response_message = "Пользователи, у которых осталось меньше 10 дней на оплату хостинга:\n"
            for user_data in users_to_notify:
                phone_number, time_web_account, last_payment_date = user_data
                response_message += f'Номер телефона: {phone_number}, Аккаунт TimeWeb: {time_web_account}, Последний день оплаты: {last_payment_date}\n'
        else:
            response_message = "Нет пользователей, у которых осталось меньше 10 дней на оплату хостинга."
        bot.send_message(message.chat.id, response_message)
    else:
        bot.send_message(message.chat.id, "Вы не являетесь менеджером.")


def update_accounts():
    try:
        # Скачиваем файл с Яндекс Диска
        y.download("/numbers.xlsx", "yandex.xlsx")
        # Читаем файл Excel
        file = pd.read_excel('./yandex.xlsx')
        # Очищаем словарь от старых записей
        accounts.clear()

        for _, row in file.iterrows():
            phone_number = str(row['Номер телефона'])
            time_web_account = row['TimeWeb аккаунт']
            tariff = convert_to_float(row['Цена тарифа'])
            last_payment_date = row['Последний день оплаты'].strftime('%Y-%m-%d')
            last_payment_date = convert_to_date(last_payment_date)
            if phone_number in accounts:
                accounts[phone_number].append({'time_web_account': time_web_account, 'tariff': tariff, 'last_payment_date': last_payment_date})
            else:
                accounts[phone_number] = [{'time_web_account': time_web_account, 'tariff': tariff, 'last_payment_date': last_payment_date}]

    except Exception as e:
        print(f'Ошибка при обновлении словаря accounts: {e}')


# Функция для запуска бота
def bot_polling():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

# Функция для планирования задач
def schedule_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Планируем выполнение функции каждый день в 9 утра
schedule.every().day.at("20:10").do(check_payment_due)
schedule.every().day.at("20:10").do(update_accounts)

# Создаем потоки для бота и планировщика
bot_thread = threading.Thread(target=bot_polling)
schedule_thread = threading.Thread(target=schedule_tasks)

# Запускаем потоки
bot_thread.start()
schedule_thread.start()

# Ожидаем завершения потока бота
bot_thread.join()
