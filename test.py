from BackEnd.database import Database

db = Database ()
print (db.getArticleInfo(1)['name'])