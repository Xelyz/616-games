import json
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
PWD = os.getenv('PASSWORD')
# Establish connection

conn = mysql.connector.connect(user='root', password=PWD, host='localhost', database='arcaeaSongInfo')
cursor = conn.cursor()

# Load JSON data
# with open('songList.json', 'r') as file:
#     data = json.load(file)['songs']

# # Insert data into database
# for song in data:
#     # # Required fields
#     # artist = song.get('artist')
#     # bpm = song.get('bpm')
#     # bpm_base = song.get('bpm_base')
#     # set_name = song.get('set')
#     # purchase = song.get('purchase')
#     # audio_preview = song.get('audioPreview')
#     # audio_preview_end = song.get('audioPreviewEnd')
#     # bg = song.get('bg')
#     # bg_inverse = song.get('bg_inverse')
#     # side = song.get('side')
#     # date = song.get('date')
#     # version = song.get('version')

#     # # Optional fields
#     # world_unlock = song.get('world_unlock', False)  # Check if the key exists

#     # cursor.execute("""
#     #     INSERT INTO songs (id, artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version, world_unlock)
#     #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     # """, (song['id'], artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version, world_unlock))
#     # song_id = cursor.lastrowid


#     # # Handle localized titles if present
#     # if 'title_localized' in song:
#     #     for lang, title in song['title_localized'].items():
#     #         cursor.execute("""
#     #             INSERT INTO localized_titles (song_id, language, title) VALUES (%s, %s, %s)
#     #         """, (song_id, lang, title))


#     # Insert difficulties, handling optional fields
#     for difficulty in song['difficulties']:
#         if(difficulty.get('audioOverride', False)):
#             cursor.execute("""
#                 SELECT * FROM songs WHERE id = %s
#             """, (song['id'],))
#             song_info = cursor.fetchone()
#             cursor.execute("""
#                 DELETE FROM difficulties WHERE song_id = %s AND rating_class = 3
#             """, (song_info[0],))
#         else:
#             continue

#         artist = difficulty.get('artist', song_info[2])
#         bpm = difficulty.get('bpm', song_info[3])
#         bpm_base = difficulty.get('bpm_base', song_info[4])
#         set_name = difficulty.get('set', song_info[5])
#         purchase = difficulty.get('purchase', song_info[6])
#         audio_preview = difficulty.get('audioPreview')
#         audio_preview_end = difficulty.get('audioPreviewEnd')
#         bg = difficulty.get('bg', song_info[10])
#         bg_inverse = difficulty.get('bg_inverse', song_info[11])
#         side = difficulty.get('side', song_info[9])
#         date = difficulty.get('date', song_info[12])
#         version = difficulty.get('version', song_info[13])

#         cursor.execute("""
#             INSERT INTO songs (id, artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (song['id'], artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version))
#         song_id = cursor.lastrowid

#         # if 'title_localized' in difficulty:
#         #     for lang, title in difficulty['title_localized'].items():
#         #         cursor.execute("""
#         #             INSERT INTO localized_titles (song_id, language, title) VALUES (%s, %s, %s)
#         #         """, (song_id, lang, title))
        
#         # chart_designer = difficulty.get('chartDesigner')
#         # jacket_designer = difficulty.get('jacketDesigner')

#         # cursor.execute("""
#         #     INSERT INTO difficulties (song_id, rating_class, chart_designer, jacket_designer, rating, date, version)
#         #     VALUES (%s, %s, %s, %s, %s, %s, %s)
#         # """, (song_id, difficulty['ratingClass'], chart_designer, jacket_designer, difficulty['rating'], date, version))
#         # cursor.execute("""
#         #     INSERT INTO difficulties (song_id, refer_to)
#         #     VALUES (%s, %s)
#         # """, (song_info[0], song_id))

# conn.commit()
# cursor.close()
# conn.close()