import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
import tempfile
from rembg import remove
from PIL import Image

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

TOKEN = '7391111599:AAHX3HXpDAABIvuv6txyvMxKyBS6Jtc3-Jw'

# Функция для удаления фона с фотографии
def remove_background(input_path, output_path):
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()

    # Удаляем фон с помощью rembg
    output_data = remove(input_data)

    with open(output_path, 'wb') as output_file:
        output_file.write(output_data)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я бот для удаления фона с фотографий.\n"
        "Просто отправьте мне фотографию, и я верну её без фона."
    )

# Обработчик фотографий
def handle_photo(update: Update, context: CallbackContext):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    logging.info(f"Получена фотография от {user.first_name} {user.last_name}")

    # Создаем временные файлы для входного и выходного изображений
    with tempfile.NamedTemporaryFile(suffix='.jpg') as input_file:
        with tempfile.NamedTemporaryFile(suffix='.png') as output_file:

            photo_file.download(input_file.name)

            update.message.reply_text("Обрабатываю изображение, пожалуйста, подождите...")


            remove_background(input_file.name, output_file.name)


            with open(output_file.name, 'rb') as f:
                update.message.reply_photo(photo=f)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher


    dp.add_handler(CommandHandler("start", start))


    dp.add_handler(MessageHandler(Filters.photo, handle_photo))


    updater.start_polling()
    logging.info("Бот запущен")
    updater.idle()

if __name__ == '__main__':
    main()

