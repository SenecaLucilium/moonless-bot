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
from BackEnd.leafFunctions.string import prepareListString, prepareListUrls, prepareListSplit, prepareCatalogPage
from BackEnd.database import Database
from BackEnd.telegraph import createTelegraph

CATALOG_KEYBOARD = {
    'back': InlineKeyboardButton ('Назад', callback_data='back'),
    'forward': InlineKeyboardButton ('Вперёд', callback_data='forward'),
    'views': InlineKeyboardButton ('Просмотры', callback_data='views'),
    'time': InlineKeyboardButton ('Время', callback_data='time')
}

class BotAPI ():
    def __init__ (self):
        self.database = Database ()
        self.currentFilters = {
            'authors': [],
            'tags': [],
            'country': [],
            'sort': 'time'
        }
        self.lastArticle = None
        self.savedCatalog = []
        self.currentIter = 0
    
        self.application = ApplicationBuilder().token(readJson(Paths.loginJSON)["TelegramAuth"]["token"]).build()

        startHandler = CommandHandler ('start', self.start)
        helpHandler = CommandHandler ('help', self.help)
        catalogConvHandler = ConversationHandler(
            entry_points=[CommandHandler("catalog", self.catalog)],
            states={
                0: [
                    CallbackQueryHandler (self.catalogBack, pattern="^" + "back" + "$"),
                    CallbackQueryHandler (self.catalogForward, pattern="^" + "forward" + "$")
                ]
            },
            fallbacks=[CommandHandler("catalog", self.catalog)]
        )
        filtersHandler = CommandHandler ('filters', self.filters)
        articleHandler = ConversationHandler(
            entry_points=[CommandHandler ('article', self.article)],
            states={
                0: [CallbackQueryHandler (self.telegraph, pattern="^" + "telegraph" + "$")]
            },
            fallbacks=[CommandHandler ('article', self.article)]
        )
        authorHandler = CommandHandler ('author', self.author)
        filterAuthorsHandler = CommandHandler ('filterAuthors', self.filterAuthors)
        filterTagsHandler = CommandHandler ('filterTags', self.filterTags)
        filterCountryHandler = CommandHandler ('filterCountry', self.filterCountry)
        uknownHandler = MessageHandler (filters.COMMAND, self.unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (catalogConvHandler)
        self.application.add_handler (filtersHandler)
        self.application.add_handler (articleHandler)
        self.application.add_handler (authorHandler)
        self.application.add_handler (filterAuthorsHandler)
        self.application.add_handler (filterTagsHandler)
        self.application.add_handler (filterCountryHandler)
        self.application.add_handler (uknownHandler)

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
            "<b>Основные команды:</b>\n"
            "/start - запуск бота\n"
            "/help - помощь и полный список команд\n"
            "/catalog - каталог статей\n"
            "/authors - авторы"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode='html'
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
            "/credentials - информация о проекте\n"
            "/filterAuthors - \n"
            "/filterTags - \n"
            "/filterCountries - \n"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )

    async def prepareCatalog (self):
        '''Подготовка '''
        pass

    async def catalog (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает первую страницу каталога.'''
        self.savedCatalog = self.database.createCatalog (self.currentFilters['authors'], self.currentFilters['tags'], self.currentFilters['country'], self.currentFilters['sort'])
        self.currentIter = 0

        keyboard = [
            [
                CATALOG_KEYBOARD['time']
            ]
        ]

        rightIter = self.currentIter + 10
        if rightIter > len (self.savedCatalog):
            rightIter = len (self.savedCatalog)
        else:
            keyboard[0].append (CATALOG_KEYBOARD['forward'])

        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "<b>Каталог:</b>\n"
            f"{prepareCatalogPage (self.savedCatalog[self.currentIter:rightIter])}"
        )

        if self.currentFilters['sort'] == 'time':
            msg += "<b>Сортировка:</b> по времени"
        else:
            msg += "<b>Сортировка:</b> по просмотрам"

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            reply_markup=reply_markup,
            parse_mode='html'
        )

        return 0

    async def catalogBack (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Реагирует на кнопку каталога "Назад"'''
        await update.callback_query.answer()
        self.currentIter -= 10

        if self.currentFilters['sort'] == 'time':
            keyboard = [[CATALOG_KEYBOARD['time']]]
        else:
            keyboard = [[CATALOG_KEYBOARD['views']]]

        if self.currentIter > 0:
            keyboard[0].append (CATALOG_KEYBOARD['back'])

        rightIter = self.currentIter + 10
        if rightIter > len (self.savedCatalog):
            rightIter = len (self.savedCatalog)
        else:
            keyboard[0].append (CATALOG_KEYBOARD['forward'])

        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "<b>Каталог:</b>\n"
            f"{prepareCatalogPage (self.savedCatalog[self.currentIter:rightIter])}"
        )

        if self.currentFilters['sort'] == 'time':
            msg += "<b>Сортировка:</b> по времени"
        else:
            msg += "<b>Сортировка:</b> по просмотрам"

        await update.callback_query.edit_message_text (text=msg, parse_mode='html')
        await update.callback_query.edit_message_reply_markup (reply_markup=reply_markup)

        return 0

    async def catalogForward (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Реагирует на кнопку каталога "Вперёд"'''
        await update.callback_query.answer()
        self.currentIter += 10

        if self.currentFilters['sort'] == 'time':
            keyboard = [[CATALOG_KEYBOARD['time']]]
        else:
            keyboard = [[CATALOG_KEYBOARD['views']]]

        if self.currentIter > 0:
            keyboard[0].append (CATALOG_KEYBOARD['back'])

        rightIter = self.currentIter + 10
        if rightIter > len (self.savedCatalog):
            rightIter = len (self.savedCatalog)
        else:
            keyboard[0].append (CATALOG_KEYBOARD['forward'])

        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "<b>Каталог:</b>\n"
            f"{prepareCatalogPage (self.savedCatalog[self.currentIter:rightIter])}"
        )

        if self.currentFilters['sort'] == 'time':
            msg += "<b>Сортировка:</b> по времени"
        else:
            msg += "<b>Сортировка:</b> по просмотрам"

        await update.callback_query.edit_message_text (text=msg, parse_mode='html')
        await update.callback_query.edit_message_reply_markup (reply_markup=reply_markup)
        
        return 0

    async def filters (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Показывает окно фильтра.'''

        authorsTmp = ""
        for author in self.currentFilters['authors']:
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
            "Текущий фильтр:\n\n"
            f"Авторы: [{authorsTmp}]\n"
            f"Теги: [{tagsTmp}]\n"
            f"Страны: [{countryTmp}]\n\n"
            "Введите команду /filterAuthors [authors] чтобы добавить/убрать авторов из фильтра.\n"
            "Введите команду /filterTags [tags] чтобы добавить/убрать теги из фильтра.\n"
            "Введите команду /filterCountry [countries] чтобы добавить/убрать страны из фильтра.\n\n"
            "При пустом фильтре будут отображаться все статьи."
        )

        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )

    async def filterAuthors (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Добавляет или удаляет автора из фильтра.'''
        if len (context.args) == 0:
            msg = (
                "Полный список авторов:\n"
                f"{prepareListSplit (self.database.getAllAuthors())}"
            )
            await update.effective_message.reply_text (msg)
        else:
            added_args = []
            denied_args = []

            for arg in context.args:
                if self.database.getAuthorInfo (arg) is None:
                    denied_args.append (arg)
                else:
                    added_args.append (arg)
            
            tempSet = set(self.currentFilters['authors'])
            tempSet.update (added_args)
            self.currentFilters['authors'] = list (tempSet)

            msg = (
                f"Принятые аргументы: {prepareListString(added_args)}\n"
                f"Не принятые аргументы: {prepareListString(denied_args)}\n"
                f"Текущий фильтр авторов: {prepareListString(self.currentFilters['authors'])}"
            )
            await update.effective_message.reply_text (msg)

    async def filterTags (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Добавляет или удаляет тег из фильтра.'''
        if len (context.args) == 0:
            msg = (
                "Полный список тегов:\n"
                f"{prepareListSplit (self.database.getAllTags())}"
            )
            await update.effective_message.reply_text (msg)
        else:
            added_args = []
            denied_args = []

            for arg in context.args:
                if (arg in self.database.getAllTags()) == False:
                    denied_args.append (arg)
                else:
                    added_args.append (arg)
            
            tempSet = set(self.currentFilters['tags'])
            tempSet.update (added_args)
            self.currentFilters['tags'] = list (tempSet)

            msg = (
                f"Принятые аргументы: {prepareListString(added_args)}\n"
                f"Не принятые аргументы: {prepareListString(denied_args)}\n"
                f"Текущий фильтр тегов: {prepareListString(self.currentFilters['tags'])}"
            )
            await update.effective_message.reply_text (msg)

    async def filterCountry (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Добавляет или удаляет страну из фильтра.'''
        if len (context.args) == 0:
            msg = (
                "Полный список стран:\n"
                f"{prepareListSplit (self.database.getAllCountries())}"
            )
            await update.effective_message.reply_text (msg)
        else:
            added_args = []
            denied_args = []

            for arg in context.args:
                if (arg in self.database.getAllCountries()) == False:
                    denied_args.append (arg)
                else:
                    added_args.append (arg)
            
            tempSet = set(self.currentFilters['country'])
            tempSet.update (added_args)
            self.currentFilters['country'] = list (tempSet)

            msg = (
                f"Принятые аргументы: {prepareListString(added_args)}\n"
                f"Не принятые аргументы: {prepareListString(denied_args)}\n"
                f"Текущий фильтр стран: {prepareListString(self.currentFilters['country'])}"
            )
            await update.effective_message.reply_text (msg)

    async def author (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Выдает информацию об авторе по id.'''
        try:
            if len (context.args) != 1:
                raise ValueError
            
            authorInfo = self.database.getAuthorInfo (context.args[0])
            if authorInfo is None:
                raise MemoryError

            msg = (
                f"<b>ID:</b> {authorInfo['id']}\n"
                f"<b>Имя:</b> {authorInfo['name']}\n"
                f"<b>Основной ресурс:</b> {authorInfo['mainLink']}\n"
                f"<b>Доп. ресурс:</b> {authorInfo['otherLink']}\n"
            )
            await update.effective_message.reply_text (msg, parse_mode='html')

        except (IndexError, ValueError) as error:
            print (f"author func error: {error}")
            await update.effective_message.reply_text ("Корректное использование: /author [id].")
        
        except MemoryError as error:
            print (f"author func error: {error}")
            await update.effective_message.reply_text ("Не существует статьи с таким id.")

    async def article (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Выдает информацию о статье по id.'''
        try:
            if len (context.args) != 1:
                raise ValueError
            
            articleInfo = self.database.getArticleInfo (int (context.args[0]))
            if articleInfo is None:
                raise MemoryError
            
            self.database.updateViewsArticle (articleInfo['id'])
            self.lastArticle = articleInfo['id']
            msg = (
                f"<b>ID:</b> {articleInfo['id']}\n"
                f"<b>Название:</b> {articleInfo['name']}\n\n"
                f"<b>Автор:</b> {articleInfo['realName']}\n"
                f"<b>Теги:</b> {prepareListString (articleInfo['tags'])}\n"
                f"<b>Страны:</b> {prepareListString (articleInfo['country'])}\n\n"
                f"<b>Дата:</b> {articleInfo['date']}\n"
                f"<b>Просмотры:</b> {articleInfo['views']}\n"
            )

            keyboard = [
                [InlineKeyboardButton ("Получить телеграф", callback_data='telegraph')]
            ]
            reply_markup = InlineKeyboardMarkup (keyboard)

            await update.effective_message.reply_text (msg, parse_mode='html', reply_markup=reply_markup)
            return 0

        except (IndexError, ValueError) as error:
            print (f"article func error: {error}")
            await update.effective_message.reply_text ("Корректное использование: /article [id].")
        
        except MemoryError as error:
            print (f"article func error: {error}")
            await update.effective_message.reply_text ("Не существует статьи с таким id.")
    
    async def telegraph (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''Возвращает ссылки на телеграф.'''
        try:
            await update.callback_query.answer()
            
            if self.lastArticle is None:
                raise Exception
            
            telegraphList = createTelegraph(self.lastArticle)['telegraph']
            msg = (
                "Полученная статья:\n"
                f"{prepareListUrls (telegraphList)}"
            )

            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text=msg
            )
        except Exception as error:
            print (f"telegraph func error: {error}")
            await update.effective_chat.reply_text ("Произошла ошибка.")