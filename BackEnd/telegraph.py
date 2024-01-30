import markdown
from telegraph import Telegraph

ARTICLE_PATH = 'C:\Main\Documents\Obsidian Vault\Moonless Project\BotTests'

def createAccount ():
    telegraph = Telegraph ()
    telegraph.create_account (
        short_name='Безлуние',
        author_name='Безлуние',
        author_url='https://t.me/moonlessLib'
    )

    return telegraph

def getArticleHTML (articleNum):
    articlePath = ARTICLE_PATH + '/{num}.md'.format (num=articleNum)

    with open (articlePath, 'r', encoding='utf-8') as file:
        text = file.read ()
        html = markdown.markdown (text)
    
    return html

def createTelegraph (articleNum):
    telegraph = createAccount ()
    
    response = telegraph.create_page (
        title='MOON_TEST',
        html_content=getArticleHTML (articleNum),
        author_name='Автор', # Вставить сюда автора
        author_url='https://t.me/vasil_topolev' # Вставить сюда линк на автора
    )

    return response