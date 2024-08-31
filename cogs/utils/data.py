import json
from dotenv import load_dotenv

class Data:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()
            cls._instance = super(Data, cls).__new__(cls)
            with open('cogs/utils/songs.json', 'r') as file:
                cls._instance.songs = json.load(file)
            with open('cogs/utils/chartConstant.json', 'r') as file:
                cls._instance.cc = json.load(file)
            with open('cogs/utils/alias.json', 'r') as file:
                cls._instance.alias = json.load(file)
        return cls._instance
    
    def reload(self):
        with open('cogs/utils/songs.json', 'r') as file:
            self.songs = json.load(file)
        with open('cogs/utils/chartConstant.json', 'r') as file:
            self.cc = json.load(file)