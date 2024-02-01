from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from ProjectSettings.paths import Paths
from BackEnd.leafFunctions.files import readJson

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Показывает короткое приветствие и отображает список основных команд.'''
    msg = (
        "Это бот, который полностью заменяет функционал сайта moonless.space в удобном формате.\n"
        "\n"
        "Бот возвращает статьи в телеграфах (telegra.ph).\n"
        "\n"
        "Основные команды:\n"
        "/start - запуск бота\n"
        "/help - помощь и полный список команд\n"
        "/catalog - каталог статей\n"
        "/authors - авторы\n"
    )
    await context.bot.sendMessage (
        chat_id=update.effective_chat.id,
        text=msg
    )

async def help (update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Показывает полный список команд.'''
    msg = (
        "Полный список команд:\n"
        "/start - запуск бота\n"
        "/help - помощь и полный список команд\n"
        "/catalog - каталог статей\n"
        "/authors - авторы\n"
        "/filters - настроить фильтры каталога\n"
        "/article [id] - получить статью по её id\n"
        "/author [id] - получить автора по его id\n"
        "/report [message] - сообщить об ошибке\n"
        "/logs - получить логи своего взаимодействия с ботом\n"
        "/credentials - информация о проекте\n"
    )
    await context.bot.sendMessage (
        chat_id=update.effective_chat.id,
        text=msg
    )

async def unknown (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage (
        chat_id=update.effective_chat.id,
        text="Неизвестно."
    )

class BotAPI ():
    def __init__ (self):
        self.application = ApplicationBuilder().token(readJson(Paths.loginJSON)["TelegramAuth"]["token"]).build()

        startHandler = CommandHandler ('start', start)
        helpHandler = CommandHandler ('help', help)
        uknownHandler = MessageHandler (filters.COMMAND, unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (uknownHandler)

        self.application.run_polling ()
