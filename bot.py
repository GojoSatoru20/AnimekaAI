

import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv

# --- Начальная настройка ---

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Конфигурация бота ---

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN_TO_SEND = os.getenv("API_TOKEN_TO_SEND")

# Проверяем, что токены загружены
if not BOT_TOKEN or not API_TOKEN_TO_SEND:
    logger.error("Ошибка: Не найдены токены в .env файле. Пожалуйста, проверьте ваш .env файл.")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# --- Клавиатуры ---

def create_token_keyboard():
    """Создает клавиатуру с кнопкой для показа токена."""
    keyboard = types.InlineKeyboardMarkup()
    show_token_button = types.InlineKeyboardButton(
        text="🔑 Показать API токен", 
        callback_data="show_token"
    )
    keyboard.add(show_token_button)
    return keyboard

# --- Обработчики команд ---

@bot.message_handler(commands=['start', 'help'])
def send_info(message: types.Message):
    """Отправляет приветственное или справочное сообщение."""
    logger.info(f"Пользователь {message.from_user.username} ({message.chat.id}) использовал команду {message.text}.")
    info_text = (
        "*Ваш личный помощник для работы с API токенами* 🤖\n\n"
        "Используйте команду /token, чтобы получить ваш персональный API токен."
    )
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['token'])
def send_token_request(message: types.Message):
    """Отправляет запрос на показ токена с кнопкой."""
    logger.info(f"Пользователь {message.from_user.username} ({message.chat.id}) запросил токен.")
    request_text = "Нажмите на кнопку ниже, чтобы сгенерировать ваш API токен."
    bot.reply_to(message, request_text, reply_markup=create_token_keyboard())

# --- Обработчики колбэков ---

@bot.callback_query_handler(func=lambda call: call.data == 'show_token')
def show_token_callback(call: types.CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Показать токен', отправляя токен в форматированном виде."""
    logger.info(f"Пользователь {call.from_user.username} ({call.message.chat.id}) сгенерировал токен.")
    
    # Формируем сообщение с токеном, удобным для копирования
    token_message = (
        f"\n"
        f"`{API_TOKEN_TO_SEND}`\n\n"
        f"_(Нажмите на токен, чтобы скопировать его)_"
    )

    # Убираем кнопку и отправляем сообщение с токеном
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=token_message,
        parse_mode='Markdown',
        reply_markup=None
    )
    
    # Отправляем пустое подтверждение, чтобы убрать "часики" с кнопки
    bot.answer_callback_query(call.id)

# --- Основная функция ---

if __name__ == '__main__':
    logger.info("Бот запускается...")
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        logger.error(f"Произошла критическая ошибка: {e}")
    finally:
        logger.info("Бот остановлен.")
