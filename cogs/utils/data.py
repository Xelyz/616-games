import pickle
from dotenv import load_dotenv

class Data:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()
            cls._instance = super(Data, cls).__new__(cls)
            with open('cogs/utils/songs.pkl', 'rb') as file:
                cls._instance.songs = pickle.load(file)
            with open('cogs/utils/alias.pkl', 'rb') as file:
                cls._instance.alias = pickle.load(file) or {}
        return cls._instance