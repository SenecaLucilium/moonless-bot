import markdown
from telegraph import Telegraph

from BackEnd.database import Database
from ProjectSettings.paths import Paths
from BackEnd.leafFunctions.files import readJson

def createAccount ():
    '''Создает аккаунт для создания статей.'''
    telegraph = Telegraph ()
    telegraph.create_account (
        short_name='Безлуние',
        author_name='Безлуние',
        author_url='https://t.me/moonlessLib'
    )

    return telegraph

def getArticleHTML (articleId) -> (str | None):
    '''По id статьи получает полный текст статьи.'''
    try:
        articlePath = readJson (Paths.loginJSON)['FilesDB']['article_path'] + '/{num}.md'.format (num=articleId)

        with open (articlePath, 'r', encoding='utf-8') as file:
            text = file.read ()
            html = markdown.markdown (text)
        
        return html
    except Exception as error:
        print (f"Error at gathering HTML: {error}")
        return None

def formatArticle (articleHTML) -> list:
    '''Форматирует HTML статьи - удаляет название и разбивает на несколько частей.'''
    articleHTML = articleHTML.replace (articleHTML.partition ('\n')[0], '', 1)[1:]
    articleHTMLList = []

    if len (articleHTML) < 20000:
        articleHTMLList.append (articleHTML)
    else:
        articleParts = articleHTML.split ('\n')

        articleLen = len(articleParts)
        articleCounter = 0
        tempHTML = ""

        while articleCounter < articleLen:
            tempHTML += articleParts [articleCounter] + '\n'
            if len (tempHTML) > 20000:
                articleHTMLList.append (tempHTML)
                tempHTML = ""
            articleCounter += 1

        if tempHTML != "":
            articleHTMLList.append (tempHTML)

    return articleHTMLList

def createTelegraphInstance (title, articleHTML, authorName, authorLink) -> list:
    '''Создает телеграф (или несколько телеграфов).'''
    telegraphList = []
    account = createAccount ()
    articleHTMLList = formatArticle (articleHTML)
    chapterCounter = 1

    for html in articleHTMLList:
        tempTitle = title
        if len (articleHTMLList) > 1:
            tempTitle += f' Ch. {chapterCounter}'

        telegraphList.append (account.create_page (
            title=tempTitle,
            html_content=html,
            author_name=authorName,
            author_url=authorLink
        ))
        
        chapterCounter += 1
    return telegraphList

def createTelegraph (articleId) -> (dict | None):
    '''По id статьи достает из базы данных полную информацию о статье, об авторе и создается телеграф.'''
    try:
        db = Database ()
        articleInfo = db.getArticleInfo (articleId)
        authorInfo = db.getAuthorInfo (articleInfo ['author'])
        telegraphList = createTelegraphInstance (articleInfo ['name'], getArticleHTML (articleId), 
                                                 authorInfo ['name'], authorInfo ['mainLink'])

        fullInfo = {
            'telegraph': telegraphList,
            'articleInfo': articleInfo,
            'authorInfo': authorInfo
        }

        return fullInfo
    except Exception as error:
        print (f"Error at creating telegraph: {error}")
        return None