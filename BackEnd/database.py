from pymongo import MongoClient
import datetime

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

    def getAuthorInfoByName (self, name):
        '''Получает информацию об авторе по имени.'''
        collection = self.client ["Moonless"]["AuthorsMeta"]
        return collection.find_one ({"name": name})

    def getAllAuthors (self):
        '''Получает список всех авторов.'''
        collection = self.client ["Moonless"]["AuthorsMeta"]
        authorsList = []

        for author in collection.find():
            authorsList.append (author ["id"])

        return authorsList

    def getAllArticles (self):
        '''Получает список всех статей.'''
        collection = self.client ["Moonless"]["ArticlesMeta"]
        return collection.find()

    def getAllCountries (self):
        '''Получает список всех стран статьи.'''
        countriesSet = set()

        for article in self.getAllArticles ():
            countriesSet.update (article['country'])
        
        return sorted(list(countriesSet))

    def getAllTags (self):
        '''Получает список всех тегов статьи.'''
        tagsSet = set()

        for article in self.getAllArticles ():
            tagsSet.update (article['tags'])
        
        return sorted(list(tagsSet))

    def updateViewsArticle (self, id):
        '''Обновляет число просмотров на статье.'''
        collection = self.client ["Moonless"]["ArticlesMeta"]
        collection.update_one ({
            'id': id
        }, {
            '$inc': {
                'views': 1
            }
        }, upsert=False)
    
    def createCatalog (self, authors, tags, country, sorting):
        collection = self.client ["Moonless"]["ArticlesMeta"]

        if len (tags) == 0:
            tags = self.getAllTags()
        if len (country) == 0:
            country = self.getAllCountries()
        if len (authors) == 0:
            authors = self.getAllAuthors()

        tempCollection = collection.find ({
            'author': {'$in': authors},
            'tags': {'$in': tags},
            'country': {'$in': country}
        })
        tempArray = []

        for article in tempCollection:
            tempArray.append (article)

        if sorting == "views":
            tempArray = self.sortViews (tempArray)
        if sorting == "time":
            tempArray = self.sortTime (tempArray)
        
        return tempArray
    
    def sortTime (self, tempArray):
        return sorted (tempArray, key=lambda i: -1 * datetime.datetime.strptime (i['date'], '%d.%m.%y').timestamp())
    
    def sortViews (self, tempArray):
        return sorted (tempArray, key=lambda i: i['views'])