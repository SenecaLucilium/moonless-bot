from BackEnd.telegraph import createTelegraph
from BackEnd.telegraph import getArticleHTML, formatArticle

from ProjectSettings.paths import Paths
from BackEnd.leafFunctions.files import readJson

# print (readJson(Paths.loginJSON)['FilesDB']['article_path'])

teleDict = createTelegraph (3)['telegraph']
for i in teleDict:
    print (i['url'])