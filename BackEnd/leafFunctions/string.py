def prepareListString (listString):
    stringTmp = ""
    for string in listString:
        stringTmp += f"{string}, "

    if stringTmp != "":
        stringTmp = stringTmp [:-2]
    return stringTmp

def prepareListSplit (listString):
    stringTmp = ""
    for string in listString:
        stringTmp += f"{string}\n"
    
    return stringTmp

def prepareListUrls (listUrls):
    stringTmp = ""
    for url in listUrls:
        stringTmp += f"{url['url']}\n"
    
    return stringTmp

def prepareCatalogPage (articleList):
    stringTmp = ""

    for article in articleList:
        tmp = (
            f"<b>Название:</b> {article['name']}\n"
            f"Автор: {article['realName']}\n"
            f"<b>ID:</b> {article['id']} | <b>Дата:</b> {article['date']} | <b>Просмотры:</b> {article['views']}"
        )

        stringTmp += (tmp + "\n\n")
    return stringTmp