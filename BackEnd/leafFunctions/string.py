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