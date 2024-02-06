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
            f"📚<b>Название:</b> {article['name']}\n"
            f"Автор: {article['realName']}\n"
            f"<b>ID:</b> {article['id']} | <b>⏳:</b> {article['date']} | <b>👁:</b> {article['views']}"
        )

        stringTmp += (tmp + "\n\n")
    return stringTmp

def prepareAuthors (authorList):
    stringTmp = ""

    for author in authorList:
        tmp = (
            f"✍️<b>ID:</b> {author['id']}\n"
            f"<b>Имя:</b> {author['name']}\n"
        )

        stringTmp += (tmp + "\n")
    return stringTmp