import sqlite3
from app import convertToBinary, parseJSON


connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

# add code to empty temp_photos

cur = connection.cursor()
parsed = parseJSON('init_db.json')

for collection in parsed['collections']:
    cur.execute("INSERT INTO gallery (title, summary) VALUES (?, ?)",
        (collection['title'], collection['summary']))

for artist in parsed['artists']:
    cur.execute("INSERT INTO artist (full_name, dob, summary) VALUES (?, ?, ?)",
        (artist['full_name'], artist['dob'], artist['summary']))

connection.commit()

for art in parsed['art']:
    query = """INSERT INTO art (title, artist, created, photo, gallery_id, summary) VALUES (?, ?, ?, ?, ?, ?)"""
    photo = convertToBinary(art['filepath'])
    collection = cur.execute('SELECT * FROM gallery WHERE title = ?', (art['collection_name'],)).fetchone()
    data_tuple = (art['title'], art['artist'], art['created'], photo, collection[0], art['summary'])
    cur.execute(query, data_tuple)

connection.commit()
connection.close()