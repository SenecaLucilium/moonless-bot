import json

def readJson (path) -> (str | None):
    '''Возвращает содержимое json как строку или пишет ошибку в терминал.'''

    with open (path, 'r', encoding='utf-8') as file:
        try:
            info = json.load (file)
            return info
        except json.JSONDecodeError as error:
            print (f"Error reading JSON: {error}")
            return None