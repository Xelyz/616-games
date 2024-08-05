import json
import mysql.connector

# Establish connection
conn = mysql.connector.connect(user='root', password='Xelyz29417', host='localhost', database='arcaeaSongInfo')
cursor = conn.cursor()

# Load JSON data
with open('songList.json', 'r') as file:
    data = json.load(file)['songs']


# Insert data into database
for song in data:
    # Required fields
    artist = song.get('artist')
    bpm = song.get('bpm')
    bpm_base = song.get('bpm_base')
    set_name = song.get('set')
    purchase = song.get('purchase')
    audio_preview = song.get('audioPreview')
    audio_preview_end = song.get('audioPreviewEnd')
    bg = song.get('bg')
    bg_inverse = song.get('bg_inverse')
    side = song.get('side')
    date = song.get('date')
    version = song.get('version')

    # Optional fields
    world_unlock = song.get('world_unlock', False)  # Check if the key exists

    cursor.execute("""
        INSERT INTO songs (id, artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version, world_unlock)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (song['id'], artist, bpm, bpm_base, set_name, purchase, audio_preview, audio_preview_end, bg, bg_inverse, side, date, version, world_unlock))
    song_id = cursor.lastrowid


    # Handle localized titles if present
    if 'title_localized' in song:
        for lang, title in song['title_localized'].items():
            cursor.execute("""
                INSERT INTO localized_titles (song_id, language, title) VALUES (%s, %s, %s)
            """, (song_id, lang, title))

    # Insert difficulties, handling optional fields
    for difficulty in song['difficulties']:
        chart_designer = difficulty.get('chartDesigner')
        jacket_designer = difficulty.get('jacketDesigner')
        rating_date = difficulty.get('date', None)
        rating_version = difficulty.get('version', None)
        cursor.execute("""
            INSERT INTO difficulties (song_id, rating_class, chart_designer, jacket_designer, rating, date, version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (song_id, difficulty['ratingClass'], chart_designer, jacket_designer, difficulty['rating'], rating_date, rating_version))

conn.commit()
cursor.close()
conn.close()