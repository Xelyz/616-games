import json
import pickle
import mysql.connector
import os
from dotenv import load_dotenv
import re

load_dotenv()
PWD = os.getenv('PASSWORD')
# Establish connection

conn = mysql.connector.connect(user='root', password=PWD, host='localhost', database='arcaeaSongInfo')
cursor = conn.cursor()

# with open('./cogs/utils/1.1.txt', 'r') as file:
#     for line in file:
#         id = re.search('Songs_(.*).jpg', line).group(1)
#         cursor.execute('''
# UPDATE songs
# SET url = %s
# WHERE id = %s;
# ''', (line.strip(), id))

cursor.execute('''
SELECT * FROM songs
''')
songs = cursor.fetchall()
data = {}
for song in songs:
    id = song[0]
    key = ['name', 'artist', 'bpm', 'bpm_base', 'set', 'purchase', 'side', 'bg', 'bg_inverse', 'version', 'world_unlock', 'jacket']
    song = dict(zip(key, song[1:]))
    cursor.execute('''
    SELECT * FROM difficulties
    WHERE song_id = %s
    ''', (id,))
    difficulties = cursor.fetchall()
    key = ['rating_class', 'chart_designer', 'jacket_designer', 'rating', 'version', 'refer_to', 'chart_constant']
    temp = []
    for diff in difficulties:
        temp.append(dict(filter(lambda x: x[1] != None,zip(key, diff[2:]))))
    song['difficulties'] = temp
    cursor.execute('''
    SELECT * FROM localized_titles
    WHERE song_id = %s
    ''', (id,))
    language, title = cursor.fetchone()[2:]
    song['language'] = language
    song['title'] = title
    data[id] = song

with open('cogs/utils/songs.pkl', 'wb') as file:
    pickle.dump(data, file)

conn.commit()
cursor.close()
conn.close()