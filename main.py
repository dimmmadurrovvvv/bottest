import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext.callbackcontext import CallbackContext
import tempfile
import pixellib
from pixellib.tune_bg import alter_bg
from PIL import Image

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


TOKEN = '7391111599:AAHX3HXpDAABIvuv6txyvMxKyBS6Jtc3-Jw'


change_bg = alter_bg()
change_bg.load_pascalvoc_model("deeplabv3_xception_tf_dim_ordering_tf_kernels.h5")


user_backgrounds = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Удалить фон", callback_data='remove_background'),
            InlineKeyboardButton("Заменить фон", callback_data='replace_background')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Привет! Я бот для удаления и замены фона с фотографий.\nВыберите, что вы хотите сделать:",
        reply_markup=reply_markup
    )

# Обработчик выбора действия
def handle_action(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'remove_background':
        query.edit_message_text(text="Отправьте фотографию, с которой нужно удалить фон.")
        context.user_data['action'] = 'remove'

    elif query.data == 'replace_background':
        query.edit_message_text(text="Сначала отправьте фотографию, которую хотите использовать в качестве нового фона.")
        context.user_data['action'] = 'replace'

# Функция для удаления фона
def remove_background(input_path, output_path):
    change_bg.color_bg(input_path, colors=(255, 255, 255), output_image_name=output_path)

# Функция для замены фона
def replace_background(input_path, output_path, background_path):
    change_bg.replace_bg(input_image_path=input_path, 
                         background_image_path=background_path, 
                         output_image_name=output_path)

def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    action = context.user_data.get('action')

    if not action:
        update.message.reply_text("Пожалуйста, сначала выберите действие: удалить фон или заменить фон.")
        return

    photo_file = update.message.photo[-1].get_file()

    # Удаление фона
    if action == 'remove':
        with tempfile.NamedTemporaryFile(suffix='.jpg') as input_file:
            with tempfile.NamedTemporaryFile(suffix='.png') as output_file:
                # Скачиваем фотографию пользователя
                photo_file.download(input_file.name)

                update.message.reply_text("Удаляю фон, пожалуйста, подождите...")


                remove_background(input_file.name, output_file.name)


                with open(output_file.name, 'rb') as f:
                    update.message.reply_photo(photo=f)


    elif action == 'replace':

        if user_id not in user_backgrounds:

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as background_file:
                photo_file.download(background_file.name)
                user_backgrounds[user_id] = background_file.name

            update.message.reply_text("Фон сохранен. Теперь отправьте фотографию, с которой нужно удалить фон.")
            context.user_data['action'] = 'replace_main_photo'

        elif action == 'replace_main_photo':
            with tempfile.NamedTemporaryFile(suffix='.jpg') as input_file:
                with tempfile.NamedTemporaryFile(suffix='.png') as output_file:

                    photo_file.download(input_file.name)

                    update.message.reply_text("Заменяю фон, пожалуйста, подождите...")

                    replace_background(input_file.name, output_file.name, user_backgrounds[user_id])

                    with open(output_file.name, 'rb') as f:
                        update.message.reply_photo(photo=f)

# Функция main
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CallbackQueryHandler(handle_action))

  
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    logging.info("Бот запущен")
    updater.idle()

if __name__ == '__main__':
    main()

