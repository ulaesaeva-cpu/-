import telebot
from telebot import types
import json
import os


TOKEN = '8657180175:AAFXYQEIg-FU6F9aQdNM1lCBJpqH79RRJBg'
ADMIN_ID = 1342747202  # ← Вставьте СВОЙ Telegram ID (узнать у @userinfobot)


bot = telebot.TeleBot(TOKEN)


DB_FILE = 'symbols.json'


# ============ РАБОТА С БАЗОЙ ============
def load_db():
    if not os.path.exists(DB_FILE):
        return {"химия": {}, "физика": {}, "математика": {}}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============ ГЛАВНОЕ МЕНЮ ============
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        types.KeyboardButton('🧪 Химия'),
        types.KeyboardButton('⚛️ Физика'),
        types.KeyboardButton('📐 Математика')
    )
    markup.add(types.KeyboardButton('ℹ️ Помощь'))
    if True:  # Админ-кнопка видна всем, но работает только для админа
        pass
    return markup


# ============ МЕНЮ КАТЕГОРИИ С СИМВОЛАМИ ============
def category_menu(category):
    db = load_db()
    symbols = list(db.get(category, {}).keys())
   
    if not symbols:
        return None
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = [types.KeyboardButton(s) for s in symbols]
    markup.add(*buttons)
    markup.add(types.KeyboardButton('⬅️ Назад'))
    return markup


# ============ ФОРМАТИРОВАНИЕ КАРТОЧКИ ============
def format_symbol(symbol, info, category=None):
    text = (
        f'🔤 Символ: <b>{symbol}</b>\n'
    )
    if category:
        text += f'📂 Категория: {category.capitalize()}\n'
    text += (
        f'\n🗣 Произносится: <b>{info["name"]}</b>\n'
        f'\n💡 Значение: {info["meaning"]}\n'
        f'\n📏 Единицы: {info["units"]}\n'
        f'\n📍 Где встречается: {info["where"]}'
    )
    return text


# ============ КОМАНДЫ ============
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f'Привет, {message.from_user.first_name}! 👋\n\n'
        'Я бот-справочник символов из <b>химии</b>, <b>физики</b> и <b>математики</b>.\n\n'
        '📌 Выбери категорию кнопкой ниже, затем нажми на символ — '
        'я расскажу, как он произносится, что значит, в чём измеряется и где встречается.\n\n'
        '💬 Или просто отправь мне символ сообщением (например, λ, π, Σ).',
        reply_markup=main_menu(),
        parse_mode='HTML'
    )


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, '⛔ У вас нет доступа к админ-панели.')
        return
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('➕ Добавить символ'),
        types.KeyboardButton('➖ Удалить символ'),
        types.KeyboardButton('📊 Статистика'),
        types.KeyboardButton('⬅️ В меню')
    )
    bot.send_message(
        message.chat.id,
        '🔧 <b>Админ-панель</b>\n\nВыберите действие:',
        reply_markup=markup,
        parse_mode='HTML'
    )


# ============ ОБРАБОТКА ТЕКСТА ============
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()
    user_id = message.from_user.id
   
    # --- Главное меню ---
    if text == '🧪 Химия':
        markup = category_menu('химия')
        if markup:
            bot.send_message(message.chat.id, '🧪 <b>Химия</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == '⚛️ Физика':
        markup = category_menu('физика')
        if markup:
            bot.send_message(message.chat.id, '⚛️ <b>Физика</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == '📐 Математика':
        markup = category_menu('математика')
        if markup:
            bot.send_message(message.chat.id, '📐 <b>Математика</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == 'ℹ️ Помощь':
        bot.send_message(
            message.chat.id,
            '📖 <b>Как пользоваться ботом</b>\n\n'
            '1. Нажми на категорию (🧪 Химия, ⚛️ Физика, 📐 Математика)\n'
            '2. Выбери символ из появившихся кнопок\n'
            '3. Получи карточку с расшифровкой\n\n'
            'Также можно просто отправить символ текстом.\n\n'
            '👨‍💻 Админ-команды: /admin',
            parse_mode='HTML',
            reply_markup=main_menu()
        )
        return
   
    if text == '⬅️ Назад' or text == '⬅️ В меню':
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=main_menu())
        return
   
    # --- Админ-панель ---
    if text == '➕ Добавить символ':
        if user_id != ADMIN_ID:
            return
        msg = bot.send_message(
            message.chat.id,
            'Введите данные в формате:\n\n'
            '<code>категория | символ | произношение | значение | единицы | где встречается</code>\n\n'
            'Пример:\n'
            '<code>физика | ħ | Аш-бар | Постоянная Планка | Дж·с | Квантовая механика</code>',
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, add_symbol_step)
        return
   
    if text == '➖ Удалить символ':
        if user_id != ADMIN_ID:
            return
        msg = bot.send_message(
            message.chat.id,
            'Введите в формате: <code>категория | символ</code>\n\n'
            'Пример: <code>физика | ħ</code>',
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, delete_symbol_step)
        return
   
    if text == '📊 Статистика':
        if user_id != ADMIN_ID:
            return
        db = load_db()
        stats = '\n'.join([f'• {k.capitalize()}: {len(v)} символов' for k, v in db.items()])
        total = sum(len(v) for v in db.values())
        bot.send_message(
            message.chat.id,
            f'📊 <b>Статистика базы</b>\n\n{stats}\n\n<b>Всего:</b> {total}',
            parse_mode='HTML'
        )
        return
   
    # --- Поиск символа ---
    db = load_db()
    symbol = text[0] if text else ''
   
    # Ищем во всех категориях
    for category, symbols in db.items():
        if text in symbols:
            bot.send_message(
                message.chat.id,
                format_symbol(text, symbols[text], category),
                parse_mode='HTML'
            )
            return
        if symbol in symbols and len(text) == 1:
            bot.send_message(
                message.chat.id,
                format_symbol(symbol, symbols[symbol], category),
                parse_mode='HTML'
            )
            return
   
    bot.send_message(
        message.chat.id,
        f'😔 Символ «{text}» не найден в базе.\n\n'
        'Попробуйте выбрать из категорий ниже 👇',
        reply_markup=main_menu()
    )


# ============ АДМИН: ДОБАВЛЕНИЕ ============
def add_symbol_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = [p.strip() for p in message.text.split('|')]
        if len(parts) != 6:
            raise ValueError('Нужно 6 частей, разделённых |')
       
        category, symbol, name, meaning, units, where = parts
        category = category.lower()
       
        if category not in ('химия', 'физика', 'математика'):
            raise ValueError('Категория должна быть: химия, физика или математика')
       
        db = load_db()
        if category not in db:
            db[category] = {}
       
        db[category][symbol] = {
            'name': name,
            'meaning': meaning,
            'units': units,
            'where': where
        }
        save_db(db)
       
        bot.send_message(
            message.chat.id,
            f'✅ Символ <b>{symbol}</b> добавлен в категорию <b>{category}</b>!',
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'❌ Ошибка: {e}\n\nПопробуйте снова через /admin',
            reply_markup=main_menu()
        )


# ============ АДМИН: УДАЛЕНИЕ ============
def delete_symbol_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = [p.strip() for p in message.text.split('|')]
        if len(parts) != 2:
            raise ValueError('Формат: категория | символ')
       
        category, symbol = parts
        category = category.lower()
       
        db = load_db()
        if category in db and symbol in db[category]:
            del db[category][symbol]
            save_db(db)
            bot.send_message(
                message.chat.id,
                f'✅ Символ <b>{symbol}</b> удалён из <b>{category}</b>.',
                parse_mode='HTML',
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                f'❌ Не найдено: {category} | {symbol}',
                reply_markup=main_menu()
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'❌ Ошибка: {e}',
            reply_markup=main_menu()
        )


# ============ ЗАПУСК ============
if __name__ == '__main__':
    print('Бот запущен...')
    bot.polling(none_stop=True)
import telebot
from telebot import types
import json
import os


TOKEN = '8657180175:AAFXYQEIg-FU6F9aQdNM1lCBJpqH79RRJBg'
ADMIN_ID = 1342747202  # ← Вставьте СВОЙ Telegram ID (узнать у @userinfobot)


bot = telebot.TeleBot(TOKEN)


DB_FILE = 'symbols.json'


# ============ РАБОТА С БАЗОЙ ============
def load_db():
    if not os.path.exists(DB_FILE):
        return {"химия": {}, "физика": {}, "математика": {}}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============ ГЛАВНОЕ МЕНЮ ============
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        types.KeyboardButton('🧪 Химия'),
        types.KeyboardButton('⚛️ Физика'),
        types.KeyboardButton('📐 Математика')
    )
    markup.add(types.KeyboardButton('ℹ️ Помощь'))
    if True:  # Админ-кнопка видна всем, но работает только для админа
        pass
    return markup


# ============ МЕНЮ КАТЕГОРИИ С СИМВОЛАМИ ============
def category_menu(category):
    db = load_db()
    symbols = list(db.get(category, {}).keys())
   
    if not symbols:
        return None
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = [types.KeyboardButton(s) for s in symbols]
    markup.add(*buttons)
    markup.add(types.KeyboardButton('⬅️ Назад'))
    return markup


# ============ ФОРМАТИРОВАНИЕ КАРТОЧКИ ============
def format_symbol(symbol, info, category=None):
    text = (
        f'🔤 Символ: <b>{symbol}</b>\n'
    )
    if category:
        text += f'📂 Категория: {category.capitalize()}\n'
    text += (
        f'\n🗣 Произносится: <b>{info["name"]}</b>\n'
        f'\n💡 Значение: {info["meaning"]}\n'
        f'\n📏 Единицы: {info["units"]}\n'
        f'\n📍 Где встречается: {info["where"]}'
    )
    return text


# ============ КОМАНДЫ ============
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f'Привет, {message.from_user.first_name}! 👋\n\n'
        'Я бот-справочник символов из <b>химии</b>, <b>физики</b> и <b>математики</b>.\n\n'
        '📌 Выбери категорию кнопкой ниже, затем нажми на символ — '
        'я расскажу, как он произносится, что значит, в чём измеряется и где встречается.\n\n'
        '💬 Или просто отправь мне символ сообщением (например, λ, π, Σ).',
        reply_markup=main_menu(),
        parse_mode='HTML'
    )


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, '⛔ У вас нет доступа к админ-панели.')
        return
   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('➕ Добавить символ'),
        types.KeyboardButton('➖ Удалить символ'),
        types.KeyboardButton('📊 Статистика'),
        types.KeyboardButton('⬅️ В меню')
    )
    bot.send_message(
        message.chat.id,
        '🔧 <b>Админ-панель</b>\n\nВыберите действие:',
        reply_markup=markup,
        parse_mode='HTML'
    )


# ============ ОБРАБОТКА ТЕКСТА ============
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()
    user_id = message.from_user.id
   
    # --- Главное меню ---
    if text == '🧪 Химия':
        markup = category_menu('химия')
        if markup:
            bot.send_message(message.chat.id, '🧪 <b>Химия</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == '⚛️ Физика':
        markup = category_menu('физика')
        if markup:
            bot.send_message(message.chat.id, '⚛️ <b>Физика</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == '📐 Математика':
        markup = category_menu('математика')
        if markup:
            bot.send_message(message.chat.id, '📐 <b>Математика</b>\nВыберите символ:',
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'В этой категории пока нет символов.')
        return
   
    if text == 'ℹ️ Помощь':
        bot.send_message(
            message.chat.id,
            '📖 <b>Как пользоваться ботом</b>\n\n'
            '1. Нажми на категорию (🧪 Химия, ⚛️ Физика, 📐 Математика)\n'
            '2. Выбери символ из появившихся кнопок\n'
            '3. Получи карточку с расшифровкой\n\n'
            'Также можно просто отправить символ текстом.\n\n'
            '👨‍💻 Админ-команды: /admin',
            parse_mode='HTML',
            reply_markup=main_menu()
        )
        return
   
    if text == '⬅️ Назад' or text == '⬅️ В меню':
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=main_menu())
        return
   
    # --- Админ-панель ---
    if text == '➕ Добавить символ':
        if user_id != ADMIN_ID:
            return
        msg = bot.send_message(
            message.chat.id,
            'Введите данные в формате:\n\n'
            '<code>категория | символ | произношение | значение | единицы | где встречается</code>\n\n'
            'Пример:\n'
            '<code>физика | ħ | Аш-бар | Постоянная Планка | Дж·с | Квантовая механика</code>',
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, add_symbol_step)
        return
   
    if text == '➖ Удалить символ':
        if user_id != ADMIN_ID:
            return
        msg = bot.send_message(
            message.chat.id,
            'Введите в формате: <code>категория | символ</code>\n\n'
            'Пример: <code>физика | ħ</code>',
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, delete_symbol_step)
        return
   
    if text == '📊 Статистика':
        if user_id != ADMIN_ID:
            return
        db = load_db()
        stats = '\n'.join([f'• {k.capitalize()}: {len(v)} символов' for k, v in db.items()])
        total = sum(len(v) for v in db.values())
        bot.send_message(
            message.chat.id,
            f'📊 <b>Статистика базы</b>\n\n{stats}\n\n<b>Всего:</b> {total}',
            parse_mode='HTML'
        )
        return
   
    # --- Поиск символа ---
    db = load_db()
    symbol = text[0] if text else ''
   
    # Ищем во всех категориях
    for category, symbols in db.items():
        if text in symbols:
            bot.send_message(
                message.chat.id,
                format_symbol(text, symbols[text], category),
                parse_mode='HTML'
            )
            return
        if symbol in symbols and len(text) == 1:
            bot.send_message(
                message.chat.id,
                format_symbol(symbol, symbols[symbol], category),
                parse_mode='HTML'
            )
            return
   
    bot.send_message(
        message.chat.id,
        f'😔 Символ «{text}» не найден в базе.\n\n'
        'Попробуйте выбрать из категорий ниже 👇',
        reply_markup=main_menu()
    )


# ============ АДМИН: ДОБАВЛЕНИЕ ============
def add_symbol_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = [p.strip() for p in message.text.split('|')]
        if len(parts) != 6:
            raise ValueError('Нужно 6 частей, разделённых |')
       
        category, symbol, name, meaning, units, where = parts
        category = category.lower()
       
        if category not in ('химия', 'физика', 'математика'):
            raise ValueError('Категория должна быть: химия, физика или математика')
       
        db = load_db()
        if category not in db:
            db[category] = {}
       
        db[category][symbol] = {
            'name': name,
            'meaning': meaning,
            'units': units,
            'where': where
        }
        save_db(db)
       
        bot.send_message(
            message.chat.id,
            f'✅ Символ <b>{symbol}</b> добавлен в категорию <b>{category}</b>!',
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'❌ Ошибка: {e}\n\nПопробуйте снова через /admin',
            reply_markup=main_menu()
        )


# ============ АДМИН: УДАЛЕНИЕ ============
def delete_symbol_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = [p.strip() for p in message.text.split('|')]
        if len(parts) != 2:
            raise ValueError('Формат: категория | символ')
       
        category, symbol = parts
        category = category.lower()
       
        db = load_db()
        if category in db and symbol in db[category]:
            del db[category][symbol]
            save_db(db)
            bot.send_message(
                message.chat.id,
                f'✅ Символ <b>{symbol}</b> удалён из <b>{category}</b>.',
                parse_mode='HTML',
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                f'❌ Не найдено: {category} | {symbol}',
                reply_markup=main_menu()
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'❌ Ошибка: {e}',
            reply_markup=main_menu()
        )


# ============ ЗАПУСК ============
if __name__ == '__main__':
    print('Бот запущен...')
    bot.polling(none_stop=True)

