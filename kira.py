import os
import subprocess
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8413125735:AAG19QW3kOSPOjfNiD4GVmFHjvbWZb5LYao"
SCRIPTS_DIR = os.path.expanduser("~/python_scripts")
processes = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Загрузить .py файл", callback_data="upload")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
    message = "Мои скрипты:\n" + "\n".join(scripts) if scripts else "Скриптов нет."
    await update.message.reply_text(message, reply_markup=reply_markup)
    logging.info(f"Пользователь {update.effective_user.id} вызвал команду /start")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data == "upload":
        await query.message.reply_text("Отправьте .py файл:")
        context.user_data["awaiting_file"] = True
        logging.info(f"Пользователь {user_id} нажал 'Загрузить .py файл'")
    elif data.startswith("script_"):
        script = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Запустить", callback_data=f"run_{script}")],
            [InlineKeyboardButton("Остановить", callback_data=f"stop_{script}")],
            [InlineKeyboardButton("Удалить", callback_data=f"delete_{script}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"Управление {script}", reply_markup=reply_markup)
        logging.info(f"Пользователь {user_id} выбрал скрипт {script}")
    elif data.startswith("run_"):
        script = data.split("_")[1]
        if script not in processes:
            try:
                process = subprocess.Popen(["python", os.path.join(SCRIPTS_DIR, script)])
                processes[script] = process
                await query.message.reply_text(f"{script} запущен.")
                logging.info(f"Пользователь {user_id} запустил скрипт {script}")
            except Exception as e:
                await query.message.reply_text(f"Ошибка при запуске {script}: {str(e)}")
                logging.error(f"Ошибка при запуске {script} пользователем {user_id}: {str(e)}")
        else:
            await query.message.reply_text(f"{script} уже запущен.")
            logging.info(f"Пользователь {user_id} попытался запустить уже запущенный скрипт {script}")
    elif data.startswith("stop_"):
        script = data.split("_")[1]
        if script in processes:
            processes[script].terminate()
            del processes[script]
            await query.message.reply_text(f"{script} остановлен.")
            logging.info(f"Пользователь {user_id} остановил скрипт {script}")
        else:
            await query.message.reply_text(f"{script} не запущен.")
            logging.info(f"Пользователь {user_id} попытался остановить не запущенный скрипт {script}")
    elif data.startswith("delete_"):
        script = data.split("_")[1]
        if script in processes:
            processes[script].terminate()
            del processes[script]
            logging.info(f"Пользователь {user_id} остановил скрипт {script} перед удалением")
        try:
            os.remove(os.path.join(SCRIPTS_DIR, script))
            await query.message.reply_text(f"{script} удалён.")
            logging.info(f"Пользователь {user_id} удалил скрипт {script}")
        except Exception as e:
            await query.message.reply_text(f"Ошибка при удалении {script}: {str(e)}")
            logging.error(f"Ошибка при удалении {script} пользователем {user_id}: {str(e)}")
        scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
        message = "Мои скрипты:\n" + "\n".join(scripts) if scripts else "Скриптов нет."
        keyboard = [[InlineKeyboardButton("Загрузить .py файл", callback_data="upload")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(message, reply_markup=reply_markup)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_file") and update.message.document:
        file = await update.message.document.get_file()
        user_id = update.effective_user.id
        if file.file_path.endswith('.py'):
            file_name = update.message.document.file_name
            file_path = os.path.join(SCRIPTS_DIR, file_name)
            try:
                await file.download_to_drive(file_path)
                process = subprocess.Popen(["python", file_path])
                processes[file_name] = process
                context.user_data["awaiting_file"] = False
                await update.message.reply_text(f"{file_name} загружен и запущен.")
                logging.info(f"Пользователь {user_id} загрузил и запустил скрипт {file_name}")
                scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
                message = "Мои скрипты:\n" + "\n".join(scripts)
                keyboard = [[InlineKeyboardButton("Загрузить .py файл", callback_data="upload")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, reply_markup=reply_markup)
            except Exception as e:
                await update.message.reply_text(f"Ошибка при загрузке/запуске {file_name}: {str(e)}")
                logging.error(f"Ошибка при загрузке/запуске {file_name} пользователем {user_id}: {str(e)}")
        else:
            await update.message.reply_text("Отправьте файл с расширением .py")
            logging.info(f"Пользователь {user_id} отправил неверный файл (не .py)")
    else:
        logging.info(f"Пользователь {user_id} отправил файл без ожидания загрузки")

async def list_scripts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
    keyboard = [[InlineKeyboardButton(script, callback_data=f"script_{script}")] for script in scripts]
    keyboard.append([InlineKeyboardButton("Загрузить .py файл", callback_data="upload")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "Мои скрипты:\n" + "\n".join(scripts) if scripts else "Скриптов нет."
    await update.message.reply_text(message, reply_markup=reply_markup)
    logging.info(f"Пользователь {update.effective_user.id} вызвал команду /list")

def main():
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_scripts))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()
