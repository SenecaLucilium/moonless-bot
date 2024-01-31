from pymongo import MongoClient

from BackEnd.leafFunctions.files import readJson
from ProjectSettings.paths import Paths

def createConnectionString () -> (str | None):
    '''Создает строку для логина в базу данных.'''
    try:
        loginInfo = readJson (Paths.loginJSON)['mongoDB']
        connectionString = f"mongodb://{loginInfo['login']}:{loginInfo['password']}@{loginInfo['ip']}:{loginInfo['port']}/"
        return connectionString
    except Exception as error:
        print (f"Error creating connection string: {error}")
        return None

class Database ():
    '''Класс для взаимодействия с базой данных.'''
    def __init__ (self):
        try:
            self.client = MongoClient (createConnectionString())
        except Exception as error:
            print (f"Error connecting into MongoDB: {error}")
            return None

    def getArticleInfo (self, id):
        '''Получает информацию о статье по id.'''
        collection = self.client ["Moonless"]["ArticlesMeta"]
        return collection.find_one ({"id": id})

    def getAuthorInfo (self, id):
        '''Получает информацию об авторе по id.'''
        collection = self.client ["Moonless"]["AuthorsMeta"]
        return collection.find_one ({"id": id})