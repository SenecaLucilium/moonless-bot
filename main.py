from article.telegraph import createTelegraph

# response = createTelegraph ('test1')
# print (response['url'])
import markdown

with open ('C:\Main\Documents\Obsidian Vault\Moonless Project\BotTests' + '/test1.md', 'r', encoding='utf-8') as file:
    text = file.read ()

    title = text.partition ('\n')[0][2:]
    print (title.encode ('utf-8'))

    html = markdown.markdown (text)