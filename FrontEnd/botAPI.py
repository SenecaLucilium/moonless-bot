from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)

from ProjectSettings.paths import Paths
from BackEnd.leafFunctions.files import readJson
from BackEnd.database import Database

class BotAPI ():
    def __init__ (self):
        self.application = ApplicationBuilder().token(readJson(Paths.loginJSON)["TelegramAuth"]["token"]).build()

        startHandler = CommandHandler ('start', self.start)
        helpHandler = CommandHandler ('help', self.help)
        catalogConvHandler = ConversationHandler(
            entry_points=[CommandHandler("catalog", self.catalog)],
            states={
                0: [
                    CallbackQueryHandler (self.catalogBack, pattern="^" + "back" + "$"),
                    CallbackQueryHandler (self.catalogSort, pattern="^" + "sort" + "$"),
                    CallbackQueryHandler (self.catalogForward, pattern="^" + "forward" + "$")
                ]
            },
            fallbacks=[CommandHandler("catalog", self.catalog)]
        )
        filterConvHandler = ConversationHandler(
            entry_points=[CommandHandler("filters", self.filters)],
            states={
                0: [
                    CallbackQueryHandler (self.filtersOver, pattern="^" + "final" + "$"),
                    CallbackQueryHandler (self.filtersAuthor, pattern="^" + "author" + "$"),
                    CallbackQueryHandler (self.filtersTags, pattern="^" + "tags" + "$"),
                    CallbackQueryHandler (self.filtersCountry, pattern="^" + "country" + "$"),
                ]
            },
            fallbacks=[CommandHandler("filters", self.filters)]
        )
        uknownHandler = MessageHandler (filters.COMMAND, self.unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (catalogConvHandler)
        self.application.add_handler (filterConvHandler)
        self.application.add_handler (uknownHandler)

        self.database = Database ()
        self.currentFilters = {
            'author': [],
            'tags': [],
            'country': []
        }

        self.application.run_polling (allowed_updates=Update.ALL_TYPES)

    @staticmethod
    async def unknown (update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает сообщение о неизвестной команде.'''
        msg = (
            "Неизвестная команда.\n"
            "Вызовите /help чтобы увидеть список доступных команд."
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )

    @staticmethod
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
            "/authors - авторы"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )

    @staticmethod
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
            "/credentials - информация о проекте"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )

    async def catalog (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает первую страницу каталога.'''

        keyboard = [
            [
                InlineKeyboardButton ("Назад", callback_data="back"),
                InlineKeyboardButton ("Время", callback_data="sort"),
                InlineKeyboardButton ("Вперёд", callback_data="forward")
            ]
        ]

        #Проверка на последнюю и первую страницу, проверка на сортировку
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "Каталог:\n"
        )
        # Вставка первых результатов каталога
        msg += (
            "Сортировка: по времени\n"
            "Фильтры:"
        )

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            reply_markup=reply_markup
        )

        return 0

    async def catalogBack (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Реагирует на кнопку каталога "Назад"'''
        await update.callback_query.answer()

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text="Назад."
        )
        return 0

    async def catalogForward (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Реагирует на кнопку каталога "Вперёд"'''
        await update.callback_query.answer()

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text="Вперед."
        )
        return 0

    async def catalogSort (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Реагирует на кнопку сортировки каталога'''
        await update.callback_query.answer()

        # await context.bot.sendMessage (
        #     chat_id=update.effective_chat.id,
        #     text="Сортировка."
        # )
        await update.callback_query.edit_message_text(
            text="Сортировка."
        )
        return 0

    def createFilterMsg (self) -> str:
        '''Возвращает строку с текущими настройками фильтра.'''

        authorsTmp = ""
        for author in self.currentFilters['author']:
            authorsTmp += f"{author}, "
        if authorsTmp != "":
            authorsTmp = authorsTmp[:-2]
        
        tagsTmp = ""
        for tag in self.currentFilters['tags']:
            tagsTmp += f"{tag}, "
        if tagsTmp != "":
            tagsTmp = tagsTmp[:-2]
        
        countryTmp = ""
        for country in self.currentFilters['country']:
            countryTmp += f"{country}, "
        if countryTmp != "":
            countryTmp = countryTmp[:-2]
        
        msg = (
            f"Текущий фильтр:\n"
            f"Авторы: [{authorsTmp}]\n"
            f"Теги: [{tagsTmp}]\n"
            f"Страны: [{countryTmp}]\n"
        )

        return msg

    async def filters (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно фильтра.'''
        msg = self.createFilterMsg ()

        keyboard = [
            [
                InlineKeyboardButton("Редактировать", callback_data="author")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            reply_markup=reply_markup
        )

        return 0
    
    async def filtersOver (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно фильтра, но не создает новое окно.'''
        query = update.callback_query
        await query.answer()

        msg = self.createFilterMsg ()

        keyboard = [
            [
                InlineKeyboardButton("Редактировать", callback_data="author")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text (
            text=msg,
            reply_markup=reply_markup
        )

        return 0
    
    async def filtersAuthor (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно с списком авторов для фильтра.'''
        query = update.callback_query
        await query.answer()

        msg = "Авторы из датабазы."

        keyboard = [
            [
                InlineKeyboardButton("Закончить", callback_data="final"),
                InlineKeyboardButton("Далее", callback_data="tags")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text (
            text=msg,
            reply_markup=reply_markup
        )

        return 0

    async def filtersTags (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно с списком тегов для фильтра.'''
        query = update.callback_query
        await query.answer()

        msg = "Теги из датабазы."

        keyboard = [
            [
                InlineKeyboardButton("Закончить", callback_data="final"),
                InlineKeyboardButton("Далее", callback_data="country")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text (
            text=msg,
            reply_markup=reply_markup
        )

        return 0

    async def filtersCountry (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно с списком стран для фильтра.'''
        query = update.callback_query
        await query.answer()

        msg = "Страны из датабазы."

        keyboard = [
            [
                InlineKeyboardButton("Закончить", callback_data="final")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text (
            text=msg,
            reply_markup=reply_markup
        )

        return 0